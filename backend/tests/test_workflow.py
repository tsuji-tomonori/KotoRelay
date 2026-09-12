"""文書から回答までの単体試験。各ケースで状態と認可境界を照合する。"""

from __future__ import annotations

import io
from uuid import uuid4

import pytest
from fastapi.testclient import TestClient
from PIL import Image

from kotorelay.context import stable_id

DEPT = stable_id("開発部")
OTHER = stable_id("営業部")


def headers(persona: str = "author", key: str | None = None) -> dict[str, str]:
    return {"Authorization": "Bearer demo-" + persona, "Idempotency-Key": key or str(uuid4())}


def create(client: TestClient, body: str = "# 開発フロー\n承認後にリリースします。") -> dict:
    response = client.post(
        "/api/documents", headers=headers(), json={"title": "開発ガイド", "department_id": DEPT}
    )
    assert response.status_code == 201, response.text
    doc = response.json()
    saved = client.put(
        f"/api/documents/{doc['id']}/draft",
        headers=headers(),
        json={"title": doc["title"], "body": body, "revision": 1},
    )
    assert saved.status_code == 200, saved.text
    return doc


def submit(client: TestClient, doc: dict) -> dict:
    revision = client.get(f"/api/documents/{doc['id']}/draft", headers=headers()).json()["revision"]
    response = client.post(
        f"/api/documents/{doc['id']}/submissions", headers=headers(), json={"revision": revision}
    )
    assert response.status_code == 201, response.text
    return response.json()


def approve(
    client: TestClient, version: dict, decision: str = "approved", reason: str = ""
) -> dict:
    reviews = client.get("/api/reviews", headers=headers("reviewer")).json()
    review = next(
        r["submission"] for r in reviews if r["submission"]["version_id"] == version["id"]
    )
    result = client.post(
        f"/api/reviews/{review['id']}/decision",
        headers=headers("reviewer"),
        json={"decision": decision, "reason": reason, "manifest_hash": version["manifest_hash"]},
    )
    assert result.status_code == 200, result.text
    return result.json()


def index(client: TestClient) -> None:
    for job in client.get("/api/operations/jobs", headers=headers("operator")).json():
        if job["status"] == "pending":
            result = client.post(f"/api/operations/jobs/{job['id']}", headers=headers("operator"))
            assert result.status_code == 200, result.text
            assert result.json()["status"] in ["done", "obsolete", "retained"]


def published(client: TestClient) -> tuple[dict, dict]:
    doc = create(client)
    version = submit(client, doc)
    approve(client, version)
    index(client)
    return doc, version


def ask(client: TestClient, persona: str = "reader", **kwargs: object):
    return client.post(
        "/api/chat",
        headers=headers(persona),
        json={"question": "開発フローの承認を教えて", "department_id": DEPT, **kwargs},
    )


def policy(client: TestClient, doc: dict, **kwargs: object):
    current = next(
        d
        for d in client.get("/api/documents?scope=manage", headers=headers("leader")).json()
        if d["id"] == doc["id"]
    )
    return client.put(
        f"/api/documents/{doc['id']}/policy",
        headers=headers("leader"),
        json={
            "revision": current["revision"],
            "visibility": "department",
            "shared_departments": [],
            "status": "active",
            **kwargs,
        },
    )


def test_保存と再読込でMarkdownを維持する(client):
    """Given 執筆権限 / When 保存・再読込 / Then 本文・保存番号が一致する。"""
    doc = create(client)
    response = client.get(f"/api/documents/{doc['id']}/draft", headers=headers())
    assert response.json()["body"] == "# 開発フロー\n承認後にリリースします。"
    assert response.json()["revision"] == 2
    assert response.headers["cache-control"] == "no-store"


def test_競合保存は先行内容を上書きしない(client):
    doc = create(client)
    result = client.put(
        f"/api/documents/{doc['id']}/draft",
        headers=headers(),
        json={"title": "改変", "body": "消えない", "revision": 1},
    )
    assert result.status_code == 409
    assert (
        client.get(f"/api/documents/{doc['id']}/draft", headers=headers())
        .json()["body"]
        .startswith("# 開発")
    )


@pytest.mark.parametrize("persona", ["reader", "leader", "other", "operator"])
def test_下書きの本文と履歴を担当外に返さない(client, persona):
    doc = create(client)
    for suffix in ["draft", "history"]:
        assert (
            client.get(f"/api/documents/{doc['id']}/{suffix}", headers=headers(persona)).status_code
            == 404
        )
    assert client.get("/api/documents?scope=work", headers=headers(persona)).json() == []


def test_未承認文書は閲覧と検索へ現れない(client):
    doc = create(client)
    submit(client, doc)
    assert client.get("/api/documents", headers=headers("reader")).json() == []
    assert client.get(f"/api/documents/{doc['id']}", headers=headers("reader")).status_code == 404
    result = ask(client).json()
    assert result["status"] == "held" and result["citations"] == []


def test_承認された版だけを引用付きで回答する(client):
    doc, version = published(client)
    result = ask(client)
    assert result.status_code == 200, result.text
    answer = result.json()
    assert answer["status"] == "answered"
    assert "承認後にリリース" in answer["answer"]
    assert answer["citations"][0]["version_id"] == version["id"]
    assert answer["citations"][0]["document_id"] == doc["id"]
    history = client.get(f"/api/chat/{answer['conversation_id']}", headers=headers("reader")).json()
    assert history[0]["answer"] == answer["answer"]


def test_却下理由と不変版を履歴に残す(client):
    doc = create(client)
    v1 = submit(client, doc)
    approve(client, v1, "rejected", "説明を追加してください")
    assert (
        client.put(
            f"/api/documents/{doc['id']}/draft",
            headers=headers(),
            json={"title": "改訂", "body": "# 開発フロー\n説明を追加。", "revision": 2},
        ).status_code
        == 200
    )
    v2 = submit(client, doc)
    assert v1["id"] != v2["id"] and v2["number"] == 2
    history = client.get(f"/api/documents/{doc['id']}/history", headers=headers()).json()
    assert history[1]["submission"]["reason"] == "説明を追加してください"
    diff = client.get(
        f"/api/documents/{doc['id']}/diff?left={v1['id']}&right={v2['id']}", headers=headers()
    ).json()
    assert "+説明を追加。" in diff["diff"] and "-承認後にリリースします。" in diff["diff"]
    assert (
        client.put(
            f"/api/documents/{doc['id']}/versions/{v1['id']}", headers=headers(), json={}
        ).status_code
        == 404
    )


def test_新しい下書きは公開タイトルと本文を変更しない(client):
    doc, v1 = published(client)
    client.put(
        f"/api/documents/{doc['id']}/draft",
        headers=headers(),
        json={"title": "極秘タイトル", "body": "公開不可", "revision": 2},
    )
    assert (
        client.get("/api/documents", headers=headers("reader")).json()[0]["title"] == "開発ガイド"
    )
    assert (
        client.get(f"/api/documents/{doc['id']}", headers=headers("reader")).json()["version"]["id"]
        == v1["id"]
    )
    assert ask(client).json()["status"] == "answered"


def test_新版承認後の未反映期間は旧版を使わない(client):
    doc, v1 = published(client)
    client.put(
        f"/api/documents/{doc['id']}/draft",
        headers=headers(),
        json={"title": "新版", "body": "開発フローを変更しました。", "revision": 2},
    )
    v2 = submit(client, doc)
    approve(client, v2)
    assert ask(client).json()["status"] == "held"
    index(client)
    assert ask(client).json()["citations"][0]["version_id"] == v2["id"]
    assert (
        client.get(
            f"/api/documents/{doc['id']}?version_id={v1['id']}", headers=headers("reader")
        ).status_code
        == 404
    )


@pytest.mark.parametrize("status", ["withdrawn", "deleted"])
def test_公開停止と削除で回答履歴も失効する(client, status):
    doc, _ = published(client)
    answer = ask(client).json()
    assert policy(client, doc, status=status).status_code == 200
    assert ask(client).json()["status"] == "held"
    history = client.get(f"/api/chat/{answer['conversation_id']}", headers=headers("reader")).json()
    assert history[0]["status"] == "hidden" and history[0]["citations"] == []
    assert "承認後にリリース" not in history[0]["answer"]


def test_他部署は直接IDと一覧とRAGから取得できない(client):
    doc, _ = published(client)
    assert client.get(f"/api/documents/{doc['id']}", headers=headers("other")).status_code == 404
    assert client.get("/api/documents", headers=headers("other")).json() == []
    assert ask(client, "other", department_id=OTHER).json()["status"] == "held"
    assert ask(client, "other").status_code == 403


def test_共有は閲覧だけを許可する(client):
    doc, _ = published(client)
    assert policy(client, doc, visibility="selected", shared_departments=[OTHER]).status_code == 200
    assert client.get(f"/api/documents/{doc['id']}", headers=headers("other")).status_code == 200
    assert (
        client.get(f"/api/documents/{doc['id']}/draft", headers=headers("other")).status_code == 404
    )
    assert (
        client.put(
            f"/api/documents/{doc['id']}/policy",
            headers=headers("other"),
            json={"revision": 1, "visibility": "organization", "status": "deleted"},
        ).status_code
        == 404
    )


def test_所属停止は古いトークンでも即時反映する(client):
    doc, _ = published(client)
    answer = ask(client).json()
    response = client.put(
        "/api/groups/memberships",
        headers=headers("leader"),
        json={"user_id": stable_id("reader"), "department_id": DEPT, "active": False},
    )
    assert response.status_code == 200
    assert client.get(f"/api/documents/{doc['id']}", headers=headers("reader")).status_code == 404
    assert (
        client.get(f"/api/chat/{answer['conversation_id']}", headers=headers("reader")).json()[0][
            "status"
        ]
        == "hidden"
    )


def test_審査の再送は結果とジョブを重複作成しない(client):
    doc = create(client)
    version = submit(client, doc)
    review = client.get("/api/reviews", headers=headers("reviewer")).json()[0]["submission"]
    key = str(uuid4())
    data = {"manifest_hash": version["manifest_hash"], "decision": "approved", "reason": ""}
    first = client.post(
        f"/api/reviews/{review['id']}/decision", headers=headers("reviewer", key), json=data
    )
    second = client.post(
        f"/api/reviews/{review['id']}/decision", headers=headers("reviewer", key), json=data
    )
    assert first.json() == second.json()
    assert len(client.get("/api/operations/jobs", headers=headers("operator")).json()) == 1
    data["decision"] = "rejected"
    data["reason"] = "不正な再送"
    assert (
        client.post(
            f"/api/reviews/{review['id']}/decision", headers=headers("reviewer", key), json=data
        ).status_code
        == 409
    )
    assert (
        client.post(
            f"/api/reviews/{review['id']}/decision", headers=headers("reviewer"), json=data
        ).status_code
        == 409
    )


def test_申請の再送で版番号を重複発行しない(client):
    doc = create(client)
    key = str(uuid4())
    url = f"/api/documents/{doc['id']}/submissions"
    a = client.post(url, headers=headers(key=key), json={"revision": 2})
    b = client.post(url, headers=headers(key=key), json={"revision": 2})
    assert a.json() == b.json()
    assert len(client.get(f"/api/documents/{doc['id']}/history", headers=headers()).json()) == 1


def test_自己承認とリーダーの暗黙承認を拒否する(client):
    doc = create(client)
    version = submit(client, doc)
    client.put(
        "/api/groups/memberships",
        headers=headers("leader"),
        json={
            "user_id": stable_id("author"),
            "department_id": DEPT,
            "can_author": True,
            "can_review": True,
        },
    )
    review = client.get("/api/reviews", headers=headers("reviewer")).json()[0]["submission"]
    for persona, code in [("author", 403), ("leader", 404)]:
        assert (
            client.post(
                f"/api/reviews/{review['id']}/decision",
                headers=headers(persona),
                json={"manifest_hash": version["manifest_hash"], "decision": "approved"},
            ).status_code
            == code
        )


@pytest.mark.parametrize(
    "data",
    [{"decision": "rejected", "reason": ""}, {"decision": "approved", "manifest_hash": "0" * 64}],
)
def test_未確認manifestと理由のない却下を拒否する(client, data):
    doc = create(client)
    version = submit(client, doc)
    review = client.get("/api/reviews", headers=headers("reviewer")).json()[0]["submission"]
    result = client.post(
        f"/api/reviews/{review['id']}/decision",
        headers=headers("reviewer"),
        json={"manifest_hash": version["manifest_hash"], **data},
    )
    assert result.status_code in [409, 422]


def test_古い版の遅着承認でも公開版は戻らない(client):
    doc = create(client)
    v1 = submit(client, doc)
    v2 = submit(client, doc)
    approve(client, v2)
    approve(client, v1)
    assert (
        client.get(f"/api/documents/{doc['id']}", headers=headers("reader")).json()["version"]["id"]
        == v2["id"]
    )


def test_閲覧と質問の再送を重複計上しない(client):
    doc, _ = published(client)
    view = {"id": str(uuid4()), "department_id": DEPT}
    assert client.post(
        f"/api/metrics/views/{doc['id']}", headers=headers("reader"), json=view
    ).json()["recorded"]
    assert not client.post(
        f"/api/metrics/views/{doc['id']}", headers=headers("reader"), json=view
    ).json()["recorded"]
    key = str(uuid4())
    question = {"question": "開発フロー", "department_id": DEPT}
    a = client.post("/api/chat", headers=headers("reader", key), json=question)
    b = client.post("/api/chat", headers=headers("reader", key), json=question)
    assert a.json() == b.json()
    metrics = client.get(
        f"/api/metrics/{DEPT}?start=2020-01-01T00:00:00Z&end=2100-01-01T00:00:00Z",
        headers=headers("leader"),
    ).json()
    assert metrics["questions"] == 1 and metrics["views"] == 1 and metrics["unique_viewers"] == 1
    assert metrics["documents"][0]["contributions"] == 1
    assert "question" not in str(metrics["documents"])


def test_他人の会話と管理統計を拒否する(client):
    published(client)
    answer = ask(client).json()
    assert (
        client.get(f"/api/chat/{answer['conversation_id']}", headers=headers("leader")).status_code
        == 404
    )
    assert ask(client, "author", conversation_id=answer["conversation_id"]).status_code == 404
    assert (
        client.get(
            f"/api/metrics/{DEPT}?start=2020-01-01T00:00:00Z&end=2100-01-01T00:00:00Z",
            headers=headers("reader"),
        ).status_code
        == 403
    )


def test_画像のOCR確認をmanifestへ固定する(client):
    doc = create(client)
    buf = io.BytesIO()
    Image.new("RGB", (40, 40), "white").save(buf, format="PNG")
    upload = client.post(
        f"/api/images/documents/{doc['id']}",
        headers=headers(),
        files={"file": ("image.png", buf.getvalue(), "image/png")},
    )
    assert upload.status_code == 201, upload.text
    asset = upload.json()["asset"]
    run = upload.json()["ocr_run"]
    p = {
        "id": str(uuid4()),
        "asset_id": asset["id"],
        "ocr_run_id": run["id"],
        "offset": 0,
        "heading": "画像",
    }
    client.put(
        f"/api/documents/{doc['id']}/draft",
        headers=headers(),
        json={"title": "画像手順", "body": "画像の開発フロー", "revision": 2, "placements": [p]},
    )
    assert (
        client.post(
            f"/api/documents/{doc['id']}/submissions", headers=headers(), json={"revision": 3}
        ).status_code
        == 409
    )
    corrected = client.post(
        f"/api/images/{asset['id']}/ocr",
        headers=headers(),
        json={
            "regions": [
                {
                    "text": "承認後に開発を開始",
                    "x": 0,
                    "y": 0,
                    "width": 1,
                    "height": 1,
                    "confidence": 1,
                    "order": 0,
                }
            ],
            "confirmed": True,
        },
    ).json()
    p["ocr_run_id"] = corrected["ocr_run"]["id"]
    client.put(
        f"/api/documents/{doc['id']}/draft",
        headers=headers(),
        json={"title": "画像手順", "body": "画像の開発フロー", "revision": 3, "placements": [p]},
    )
    version = submit(client, doc)
    approve(client, version)
    index(client)
    assert (
        client.get(
            f"/api/images/{asset['id']}?version_id={version['id']}", headers=headers("reader")
        ).status_code
        == 200
    )
    assert client.get(f"/api/images/{asset['id']}", headers=headers("reader")).status_code == 404
    assert (
        client.get(
            f"/api/images/ocr/{run['id']}?version_id={version['id']}", headers=headers("reader")
        ).status_code
        == 404
    )
    assert ask(client).json()["status"] == "answered"


@pytest.mark.parametrize("payload", [b"", b"<svg onload=alert(1)>", b"not-a-png"])
def test_不正画像を拒否する(client, payload):
    doc = create(client)
    assert (
        client.post(
            f"/api/images/documents/{doc['id']}",
            headers=headers(),
            files={"file": ("bad.png", payload, "image/png")},
        ).status_code
        == 422
    )


@pytest.mark.parametrize("token", ["", "Bearer invalid", "Bearer demo-missing"])
def test_未認証要求を拒否する(client, token):
    assert client.get("/api/documents", headers={"Authorization": token}).status_code == 401


def test_認可情報の上書き入力を拒否する(client):
    result = client.post(
        "/api/documents",
        headers=headers(),
        json={"title": "無効", "department_id": DEPT, "can_author": True},
    )
    assert result.status_code == 422 and "can_author" not in result.text
    assert client.get("/api/health").json()["product"] == "KotoRelay"


def test_非運用者は反映ジョブを操作できない(client):
    assert client.get("/api/operations/jobs", headers=headers("reader")).status_code == 403
    assert client.get("/api/operations/reconcile", headers=headers("leader")).status_code == 403
