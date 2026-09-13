"""文書から回答までの単体試験。各ケースで状態と認可境界を照合する。"""

from __future__ import annotations

import io
from uuid import uuid4

import pytest
from fastapi.testclient import TestClient
from kotorelay.context import stable_id
from PIL import Image

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
            "reason": "検証文書の利用終了",
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

    assert client.get(f"/api/images/ocr/{p['ocr_run_id']}", headers=headers()).status_code == 200
    rt = client.app.state.runtime
    rt.settings.max_model_images = 0
    assert ask(client).status_code == 200
    rt.settings.max_model_images = 5
    assert ask(client).status_code == 200
    policy(client, doc, status="deleted")
    rt.settings.retention_days = 0
    index(client)


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


def test_現行の所属と管理メンバーを取得する(client):
    me = client.get("/api/groups/me", headers=headers("author")).json()
    assert me["user"]["display_name"] == "青木 はるか"
    members = client.get(f"/api/groups/{DEPT}/members", headers=headers("leader")).json()
    assert len(members) == 5
    assert client.get(f"/api/groups/{DEPT}/members", headers=headers("reader")).status_code == 403
    assert (
        client.put(
            "/api/groups/memberships",
            headers=headers("operator"),
            json={"user_id": stable_id("other"), "department_id": DEPT, "can_author": True},
        ).status_code
        == 200
    )
    assert (
        client.get("/api/groups/me", headers=headers("other")).json()["memberships"][1][
            "can_author"
        ]
        is True
    )


def test_反映失敗を照合し再試行で回復する(client, monkeypatch):
    doc = create(client)
    version = submit(client, doc)
    approve(client, version)
    differences = client.get("/api/operations/reconcile", headers=headers("operator")).json()
    assert differences[0]["reason"] == "最新承認版が未反映"
    rt = client.app.state.runtime
    monkeypatch.setattr(rt.engine, "verify", lambda keys: False)
    job = client.get("/api/operations/jobs", headers=headers("operator")).json()[0]
    result = client.post(f"/api/operations/jobs/{job['id']}", headers=headers("operator")).json()
    assert result["status"] == "failed"
    assert ask(client).json()["status"] == "held"
    monkeypatch.setattr(rt.engine, "verify", lambda keys: True)
    result = client.post(f"/api/operations/jobs/{job['id']}", headers=headers("operator")).json()
    assert result["status"] == "done"
    assert ask(client).json()["status"] == "answered"
    assert (
        client.post(f"/api/operations/jobs/{job['id']}", headers=headers("operator")).json()[
            "attempts"
        ]
        == 2
    )
    policy(client, doc, status="withdrawn")
    assert (
        "停止済み"
        in client.get("/api/operations/reconcile", headers=headers("operator")).json()[0]["reason"]
    )
    index(client)


def test_画像を含む削除を保持期間後に完了する(client, db):
    doc, _ = published(client)
    answer = ask(client).json()
    assert policy(client, doc, status="deleted").status_code == 200
    jobs = client.get("/api/operations/jobs", headers=headers("operator")).json()
    purge = next(j for j in jobs if j["kind"] == "purge")
    url = f"/api/operations/jobs/{purge['id']}"
    assert client.post(url, headers=headers("operator")).json()["status"] == "retained"
    client.app.state.runtime.settings.retention_days = 0
    assert client.post(url, headers=headers("operator")).json()["status"] == "done"
    assert not any(c["document_id"] == doc["id"] for c in db.tables["chunks"].values())
    assert not any(d["document_id"] == doc["id"] for d in db.tables["drafts"].values())
    assert (
        client.get(f"/api/chat/{answer['conversation_id']}", headers=headers("reader")).json()[0][
            "status"
        ]
        == "hidden"
    )


def test_モデル実行中の権限変更で回答を保留する(client, monkeypatch):
    import query_helpers as q
    from kotorelay.operations.documents.change_policy.functions import policy as update
    from kotorelay.operations.documents.change_policy.schemas import ChangePolicy

    doc, _ = published(client)
    rt = client.app.state.runtime

    def generate(question, texts, images):
        with rt.context("demo-leader") as ctx:
            current = q.documents_get(ctx.db, ctx.org, doc["id"])[0]
            update(
                ctx,
                doc["id"],
                ChangePolicy(
                    revision=current.revision, visibility="department", status="withdrawn"
                ),
            )
        return "絶対に送信しない本文"

    monkeypatch.setattr(rt.engine, "generate", generate)
    result = ask(client).json()
    assert result["status"] == "held" and "絶対に送信" not in result["answer"]


def test_モデル呼び出し失敗を失敗件数として区別する(client, monkeypatch):
    published(client)

    def generate(*args):
        raise TimeoutError("timeout")

    monkeypatch.setattr(client.app.state.runtime.engine, "generate", generate)
    result = ask(client).json()
    assert result["status"] == "failed" and result["citations"] == []


def test_不正な索引来歴をモデルへ渡さない(client, db):
    doc, _ = published(client)
    chunk = next(iter(db.tables["chunks"].values()))
    chunk["manifest_hash"] = "0" * 64
    assert ask(client).json()["status"] == "held"
    chunk["manifest_hash"] = ""
    chunk["body_key"] = "0" * 64
    assert ask(client).json()["status"] == "held"


def test_利用上限を超えた質問を受け付けない(client):
    client.app.state.runtime.settings.max_questions_per_day = 1
    assert ask(client).status_code == 200
    assert ask(client).status_code == 429


def test_失効したジョブは公開版を戻さない(client):
    doc = create(client)
    v1 = submit(client, doc)
    approve(client, v1)
    v2 = submit(client, doc)
    approve(client, v2)
    jobs = client.get("/api/operations/jobs", headers=headers("operator")).json()
    old = next(j for j in jobs if j["version_id"] == v1["id"])
    assert (
        client.post(f"/api/operations/jobs/{old['id']}", headers=headers("operator")).json()[
            "status"
        ]
        == "obsolete"
    )
    index(client)
    assert ask(client).json()["citations"][0]["version_id"] == v2["id"]


def test_外部索引失敗を記録して部分完了をreadyにしない(client, monkeypatch):
    doc = create(client)
    version = submit(client, doc)
    approve(client, version)

    def index_failure(*args):
        raise OSError("external")

    monkeypatch.setattr(client.app.state.runtime.engine, "index", index_failure)
    job = client.get("/api/operations/jobs", headers=headers("operator")).json()[0]
    result = client.post(f"/api/operations/jobs/{job['id']}", headers=headers("operator")).json()
    assert result["status"] == "failed" and result["error_code"] == "external_failure"
    assert ask(client).json()["status"] == "held"


def test_workerが未配送ジョブを処理する(client):
    from kotorelay.worker import run_once

    doc = create(client)
    version = submit(client, doc)
    approve(client, version)
    assert run_once(client.app.state.runtime) == 1
    assert run_once(client.app.state.runtime) == 0
    assert ask(client).json()["status"] == "answered"


@pytest.mark.parametrize(
    "target", ["document", "version", "chunk", "manifest", "placement", "body"]
)
def test_回答根拠の欠落と改変は閲覧時に非表示とする(client, db, target):
    doc, version = published(client)
    answer = ask(client).json()
    chunk = db.tables["chunks"][answer["citations"][0]["chunk_id"]]
    if target == "document":
        del db.tables["documents"][doc["id"]]
    elif target == "version":
        del db.tables["versions"][version["id"]]
    elif target == "chunk":
        del db.tables["chunks"][chunk["id"]]
    elif target == "manifest":
        db.tables["versions"][version["id"]]["manifest"] = "{}"
    elif target == "placement":
        chunk["placements"] = '["unknown"]'
    else:
        client.app.state.runtime.objects.delete(chunk["body_key"])
    result = client.get(f"/api/chat/{answer['conversation_id']}", headers=headers("reader")).json()
    assert result[0]["status"] == "hidden" and result[0]["citations"] == []


def test_中断した質問は同じIDで再開し二重計上しない(client, db):
    from kotorelay.operations.chat.ask_question.functions import prepare
    from kotorelay.operations.chat.ask_question.schemas import Ask

    published(client)
    rt = client.app.state.runtime
    key = str(uuid4())
    data = Ask(question="開発フロー", department_id=DEPT)
    with rt.context("demo-reader") as ctx:
        first = prepare(ctx, data, key, rt.engine)
    result = client.post("/api/chat", headers=headers("reader", key), json=data.model_dump())
    assert result.status_code == 200, result.text
    assert result.json()["conversation_id"] == first.conversation_id
    assert len([e for e in db.tables["events"].values() if e["kind"] == "question"]) == 1


def test_外部検索は返されたID以外を根拠にしない(client, monkeypatch):
    published(client)
    rt = client.app.state.runtime
    monkeypatch.setattr(rt.engine, "search", lambda *args: [])
    assert ask(client).json()["status"] == "held"


def test_モデル入力直前に失効を検知した場合はモデルを呼ばない(client, monkeypatch):
    from kotorelay.operations.chat.ask_question import functions as service

    published(client)
    original = service.validate_citation
    calls = 0

    def validate(ctx, citation):
        nonlocal calls
        calls += 1
        return original(ctx, citation) if calls == 1 else False

    monkeypatch.setattr(service, "validate_citation", validate)
    assert ask(client).json()["status"] == "held"


def test_削除配送を100行単位で再開し共有本文を残す(client, db):
    from kotorelay.worker import run_once

    doc, _ = published(client)
    other, _ = published(client)
    chunk = next(c for c in db.tables["chunks"].values() if c["document_id"] == doc["id"])
    for _ in range(101):
        new = dict(chunk, id=str(uuid4()))
        db.tables["chunks"][new["id"]] = new
    policy(client, doc, status="deleted")
    rt = client.app.state.runtime
    rt.settings.retention_days = 0
    run_once(rt)
    run_once(rt)
    assert not [c for c in db.tables["chunks"].values() if c["document_id"] == doc["id"]]
    assert client.get(f"/api/documents/{other['id']}", headers=headers("reader")).status_code == 200


def test_HTTP処理ログを通常のINFO設定で出力し本文とトークンを含めない(client, caplog):
    create(client, body="ログへ出さない架空の機密本文")
    messages = [record.getMessage() for record in caplog.records if record.name == "kotorelay"]
    assert messages and all("request_id=" in message for message in messages)
    assert "ログへ出さない" not in "".join(messages)
    assert "demo-author" not in "".join(messages)
