"""UIの取り違え防止に必要なAPI契約を検証する。"""

import io
import json
from uuid import uuid4

import query_helpers as q
from PIL import Image
from test_workflow import DEPT, OTHER, approve, ask, create, headers, policy, published, submit


def grant(client, persona, department, **permissions):
    user = client.get("/api/groups/me", headers=headers(persona)).json()["user"]["id"]
    response = client.put(
        "/api/groups/memberships",
        headers=headers("operator"),
        json={"user_id": user, "department_id": department, **permissions},
    )
    assert response.status_code == 200


def department_page_case(client):
    grant(client, "leader", OTHER, leader=True)
    grant(client, "other", OTHER, can_author=True)
    first = create(client)
    second = client.post(
        "/api/documents",
        headers=headers("other"),
        json={"title": "営業部の文書", "department_id": OTHER},
    ).json()
    for department, expected in [(DEPT, first["id"]), (OTHER, second["id"])]:
        response = client.get(
            f"/api/documents?scope=manage&page=true&department_id={department}&limit=1",
            headers=headers("leader"),
        )
        assert response.status_code == 200, response.text
        assert [d["id"] for d in response.json()["items"]] == [expected]
        assert response.json()["has_next"] is False
    assert (
        client.get(
            f"/api/documents?scope=work&department_id={OTHER}", headers=headers("author")
        ).status_code
        == 403
    )
    assert (
        client.get(
            f"/api/documents?scope=manage&department_id={DEPT}", headers=headers("reader")
        ).status_code
        == 403
    )


def test_複数部署の一覧を権限検査してページング前に絞る(client):
    """Given: 複数部署の管理権限と各部署の文書がある。
    When: 部署を指定し1件ずつの管理一覧を取得する。
    Then: ページング前に部署で絞り、権限のない部署や用途は403で拒否する。
    """
    department_page_case(client)


def test_一覧は公開版と審査版を分離し続きの有無を返す(client):
    """Given: 公開版と未承認の新版があり、複数の下書きもある。
    When: 閲覧・執筆・管理一覧をページングと検索で取得する。
    Then: 公開情報と審査情報を混ぜず、続きの有無・状態・検索結果を正しく返す。
    """
    doc, version = published(client)
    current = client.get(f"/api/documents/{doc['id']}/draft", headers=headers()).json()
    client.put(
        f"/api/documents/{doc['id']}/draft",
        headers=headers(),
        json={"title": "未承認タイトル", "body": "未承認本文", "revision": current["revision"]},
    )
    next_version = submit(client, doc)
    read = client.get("/api/documents?page=true", headers=headers("reader")).json()["items"][0]
    assert read["title"] == version["title"] and "未承認" not in read["summary"]
    assert read["published_number"] == 1 and read["index_ready"] is True
    assert read["review_status"] is None and read["approved_at"]
    work = client.get("/api/documents?scope=work&page=true", headers=headers()).json()["items"][0]
    assert work["review_number"] == next_version["number"] and work["review_status"] == "pending"
    create(client)
    assert (
        client.get("/api/documents?scope=work&page=true&limit=1", headers=headers()).json()[
            "has_next"
        ]
        is True
    )
    assert (
        client.get(
            "/api/documents?scope=work&page=true&limit=1&offset=1", headers=headers()
        ).json()["has_next"]
        is False
    )
    policy(client, doc, status="withdrawn")
    filtered = client.get(
        "/api/documents?scope=manage&page=true&status=withdrawn", headers=headers("leader")
    ).json()
    assert [d["id"] for d in filtered["items"]] == [doc["id"]]
    assert client.get(
        "/api/documents?page=true&search=不存在", headers=headers("reader")
    ).json() == {"items": [], "has_next": False}


def test_削除は理由必須で状態変更と同じtransactionに監査を残す(client, db):
    """Given: 有効な文書がある。
    When: 空の理由で削除し、続いて理由付きで削除する。
    Then: 理由なしは422で状態を維持し、理由ありは状態変更と監査を1回だけ保存する。
    """
    doc = create(client)
    assert policy(client, doc, status="deleted", reason="  ").status_code == 422
    assert db.tables["documents"][doc["id"]]["status"] == "active"
    response = policy(client, doc, status="deleted", reason="利用終了のため")
    assert response.status_code == 200
    audit = [a for a in db.tables["audit"].values() if a["action"] == "policy"]
    assert len(audit) == 1 and audit[0]["reason"] == "利用終了のため"


def test_会話内の利用部署変更を拒否し新規会話なら許可する(client):
    """Given: 利用者が複数部署に所属し、既存の会話がある。
    When: 同じ会話で部署を変え、その後新しい会話で別部署を指定する。
    Then: 既存会話の部署変更は409、新規会話は別IDで200となる。
    """
    published(client)
    grant(client, "reader", OTHER)
    first = ask(client).json()
    assert ask(client, conversation_id=first["conversation_id"]).status_code == 200
    changed = ask(client, conversation_id=first["conversation_id"], department_id=OTHER)
    assert changed.status_code == 409
    fresh = ask(client, department_id=OTHER)
    assert fresh.status_code == 200 and fresh.json()["conversation_id"] != first["conversation_id"]


def upload(client, doc):
    buf = io.BytesIO()
    Image.new("RGB", (20, 20), "white").save(buf, format="PNG")
    return client.post(
        f"/api/images/documents/{doc['id']}",
        headers=headers(),
        files={"file": ("x.png", buf.getvalue(), "image/png")},
    ).json()


def test_OCR領域の複数行訂正と削除追加でも識別座標を保つ(client):
    """Given: 画像のOCRに識別子と座標付きの領域がある。
    When: 複数行訂正・領域削除・追加を行い、過去のOCRと重複ID入力も確認する。
    Then: 識別子と座標を保ち、人の訂正として記録し、過去のOCRは不変、重複IDは422となる。
    """
    doc = create(client)
    asset = upload(client, doc)["asset"]
    ids = [str(uuid4()), str(uuid4())]
    regions = [
        {
            "region_id": rid,
            "text": str(i),
            "x": i * 0.3,
            "y": 0.1,
            "width": 0.2,
            "height": 0.2,
            "confidence": 0.8,
            "order": i,
        }
        for i, rid in enumerate(ids)
    ]

    def correct(values):
        response = client.post(
            f"/api/images/{asset['id']}/ocr",
            headers=headers(),
            json={"regions": values, "confirmed": True},
        )
        assert response.status_code == 200, response.text
        return response.json()

    first = correct(regions)
    last = correct(
        [
            {**regions[1], "text": "複数行\n訂正内容", "order": 0},
            {
                **regions[0],
                "region_id": str(uuid4()),
                "text": "追加",
                "confidence": None,
                "source": "human",
                "order": 1,
            },
        ]
    )
    value = last["ocr"]["regions"][0]
    assert (
        value["region_id"] == ids[1] and value["x"] == 0.3 and (value["text"] == "複数行\n訂正内容")
    )
    assert value["confidence"] is None and value["source"] == "human"
    before = client.get(f"/api/images/ocr/{first['ocr_run']['id']}", headers=headers()).json()
    assert before["regions"][0]["text"] == "0" and before["confirmed"] is True
    duplicate = client.post(
        f"/api/images/{asset['id']}/ocr",
        headers=headers(),
        json={"regions": [regions[0], regions[0]], "confirmed": True},
    )
    assert duplicate.status_code == 422


def test_旧OCRの読取は安定IDを補うだけで保存済みハッシュを変えない(client, db):
    """Given: 領域識別子のない旧形式OCRを保存している。
    When: 同じOCRを2回取得して保存済み実体も読む。
    Then: 同じ安定IDを補い、保存済みハッシュと元の内容は変更しない。
    """
    doc = create(client)
    uploaded = upload(client, doc)
    rid = uploaded["ocr_run"]["id"]
    with client.app.state.runtime.context("demo-author") as ctx:
        value = {
            "engine": "legacy",
            "status": "ready",
            "regions": [
                {
                    "text": "以前の領域",
                    "x": 0,
                    "y": 0,
                    "width": 1,
                    "height": 1,
                    "confidence": 0.5,
                    "order": 0,
                }
            ],
        }
        key = ctx.objects.put(json.dumps(value).encode())
        db.tables["ocr_runs"][rid].update({"result_key": key, "result_hash": key})
    first = client.get(f"/api/images/ocr/{rid}", headers=headers()).json()
    second = client.get(f"/api/images/ocr/{rid}", headers=headers()).json()
    assert first["regions"][0]["region_id"] == second["regions"][0]["region_id"]
    with client.app.state.runtime.context("demo-author") as ctx:
        assert (
            q.ocr_runs_get(ctx.db, q.OcrRunsGetParams(organization_id=ctx.org, id=rid))[
                0
            ].result_hash
            == key
        )
        assert json.loads(ctx.objects.get(key)) == value


def test_代替テキストと絵文字位置を承認版へ固定する(client):
    """Given: 絵文字を含む本文に画像配置と代替テキストがある。
    When: 承認後に下書きの代替テキストを変更する。
    Then: 承認版は当時の配置・コードポイント位置・代替テキストを保持する。
    """
    doc = create(client)
    data = upload(client, doc)
    run = client.post(
        f"/api/images/{data['asset']['id']}/ocr",
        headers=headers(),
        json={"regions": [], "confirmed": True},
    ).json()["ocr_run"]
    placement = {
        "id": str(uuid4()),
        "asset_id": data["asset"]["id"],
        "ocr_run_id": run["id"],
        "offset": 2,
        "heading": "手順",
        "alt_text": "受付から承認へ進む図",
        "caption": "業務の流れ",
    }
    saved = client.put(
        f"/api/documents/{doc['id']}/draft",
        headers=headers(),
        json={"title": "画像手順", "body": "日😀本文", "revision": 2, "placements": [placement]},
    )
    assert saved.status_code == 200
    version = submit(client, doc)
    approve(client, version)
    assert json.loads(version["manifest"])["images"][0]["placement"] == placement
    placement["alt_text"] = "次版の説明"
    client.put(
        f"/api/documents/{doc['id']}/draft",
        headers=headers(),
        json={"title": "次版", "body": "日😀本文", "revision": 3, "placements": [placement]},
    )
    old = client.get(f"/api/documents/{doc['id']}", headers=headers("reader")).json()
    assert (
        json.loads(old["version"]["manifest"])["images"][0]["placement"]["alt_text"]
        == "受付から承認へ進む図"
    )


def test_審査とジョブの表示名を対象版から得る(client):
    """Given: 承認済み版と未承認のタイトルがある。
    When: 審査とジョブの詳細一覧を取得する。
    Then: 対象版の表示名と版番号を返し、未承認名を混ぜず、運用権限のない詳細取得は403となる。
    """
    doc, version = published(client)
    client.put(
        f"/api/documents/{doc['id']}/draft",
        headers=headers(),
        json={"title": "未承認名", "body": "本文", "revision": 2},
    )
    review = client.get("/api/reviews", headers=headers("reviewer")).json()[0]
    assert review["title"] == version["title"] and review["version_number"] == 1
    assert review["requested_by"] and review["department_name"]
    jobs = client.get("/api/operations/jobs?details=true", headers=headers("operator")).json()
    assert jobs[0]["version_number"] == 1
    assert (
        client.get("/api/operations/jobs?details=true", headers=headers("reader")).status_code
        == 403
    )
    fresh = create(client)
    policy(client, fresh, status="deleted")
    jobs = client.get("/api/operations/jobs?details=true", headers=headers("operator")).json()
    assert any(j["version_number"] is None for j in jobs)


def test_Markdownの空白改行を保存してコードポイント位置を維持する(client):
    """Given: 空白・改行・絵文字を含むMarkdownがある。
    When: タイトルと本文を保存し、空白だけのタイトルでも保存を試す。
    Then: 本文をそのまま維持し、タイトルだけを整形し、空タイトルは422で拒否する。
    """
    doc = create(client)
    body = "  日😀\n\n    コード\n\n"
    saved = client.put(
        f"/api/documents/{doc['id']}/draft",
        headers=headers(),
        json={"title": "  手順  ", "body": body, "revision": 2},
    )
    assert saved.status_code == 200
    assert saved.json()["body"] == body and saved.json()["document"]["title"] == "手順"
    invalid = client.put(
        f"/api/documents/{doc['id']}/draft",
        headers=headers(),
        json={"title": "  ", "body": body, "revision": 3},
    )
    assert invalid.status_code == 422
