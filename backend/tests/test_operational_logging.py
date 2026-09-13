"""例外応答と型付き運用ログの対応・機密保護を実HTTPで確認する。"""

import json
from uuid import UUID

import psycopg
import pytest
from botocore.exceptions import ClientError
from kotorelay.errors import Problem
from kotorelay.operational_logging import (
    CATALOG,
    MessageId,
    OperationalLogContext,
    continuation_context,
    ops_logger,
)
from pydantic import ValidationError
from test_workflow import DEPT, ask, create, headers, published


def records(caplog):
    return [json.loads(r.getMessage()) for r in caplog.records if r.name == "kotorelay.operations"]


@pytest.mark.parametrize(
    ("error", "status", "code", "message"),
    [
        (
            Problem(403, "forbidden", "この操作は許可されていません。"),
            403,
            "forbidden",
            "この操作は許可されていません。",
        ),
        (
            Problem(503, "integrity", "保存内容の整合性を確認できません。"),
            503,
            "integrity",
            "保存内容の整合性を確認できません。",
        ),
        (
            psycopg.errors.SerializationFailure("秘密のSQL"),
            409,
            "conflict",
            "競合しました。再読込してください。",
        ),
        (
            psycopg.errors.UniqueViolation("秘密の値"),
            409,
            "conflict",
            "競合しました。再読込してください。",
        ),
        (
            psycopg.OperationalError("秘密の接続文字列"),
            503,
            "unavailable",
            "一時的に利用できません。",
        ),
        (
            ClientError({"Error": {"Code": "Denied", "Message": "秘密の本文"}}, "Search"),
            503,
            "unavailable",
            "一時的に利用できません。",
        ),
        (OSError("秘密のパス"), 503, "unavailable", "一時的に利用できません。"),
    ],
    ids=[
        "認可拒否",
        "実体不整合",
        "更新競合",
        "重複制約",
        "DB停止",
        "外部サービス拒否",
        "実体読取失敗",
    ],
)
def test_例外型とHTTP応答を同じ相関IDのログに記録する(client, caplog, error, status, code, message):
    """Given: 業務・DB・外部依存先が既知の例外を送出する。
    When: HTTPで処理を要求し、応答と運用ログを取得する。
    Then: 例外型とstatus・code・message・相関IDが一致し、依存先の秘密の生メッセージを含めない。
    """

    def fail():
        raise error

    client.app.add_api_route("/api/log-probe", fail)
    response = client.get("/api/log-probe")
    body = response.json()
    assert response.status_code == status, "例外分類に対応するHTTP statusを返す。"
    assert body == {
        "code": code,
        "message": message,
        "request_id": response.headers["x-request-id"],
    }
    entry = records(caplog)[-1]
    assert entry["context"] == {"exception_type": type(error).__name__, "status": status, **body}
    assert entry["level"] == ("ERROR" if status >= 500 else "WARNING")
    assert entry["check_procedure"] and entry["remediation_procedure"]
    assert "秘密" not in json.dumps(entry, ensure_ascii=False)
    assert UUID(body["request_id"])


def test_入力と認証の拒否を安全な応答とログで照合する(client, caplog):
    """Given: 未認証の要求と、余剰の機密項目を含む入力がある。
    When: 一覧取得と不正な文書作成を要求する。
    Then: 401と422を返し、ログには入力値を反射せず応答コードと例外型を残す。
    """
    unauthorized = client.get("/api/documents")
    invalid = client.post(
        "/api/documents",
        headers=headers(),
        json={"department_id": DEPT, "title": "試験", "password": "秘密"},
    )
    assert [unauthorized.status_code, invalid.status_code] == [401, 422]
    assert [(r["context"]["exception_type"], r["context"]["code"]) for r in records(caplog)] == [
        ("Problem", "unauthenticated"),
        ("RequestValidationError", "invalid_input"),
    ]
    assert "秘密" not in json.dumps(records(caplog), ensure_ascii=False)


def test_型やcatalogの規約を満たさないログを拒否する():
    """Given: 運用ログに必要な独自型とcatalogがある。
    When: 辞書・未知項目・未登録ID・誤ったlevelでログを出そうとする。
    Then: 型や値のエラーとして拒否し、不完全な運用ログを記録しない。
    """
    context = continuation_context(MessageId.MODEL_FAILED, TimeoutError("秘密"))
    assert context.message == CATALOG[MessageId.MODEL_FAILED].response
    with pytest.raises(TypeError):
        ops_logger.error(MessageId.MODEL_FAILED, context_model={})
    with pytest.raises(TypeError):
        ops_logger.error("unknown", context_model=context)
    with pytest.raises(ValueError):
        ops_logger.warning(MessageId.MODEL_FAILED, context_model=context)
    with pytest.raises(ValidationError):
        OperationalLogContext(**context.model_dump(), token="秘密")
    with pytest.raises(ValidationError):
        OperationalLogContext(request_id=None, status=None, code=None, message="安全な説明")


def test_モデル失敗は継続結果をログに記録しHTTP200で失敗状態を返す(client, monkeypatch, caplog):
    """Given: 公開・索引反映済みの根拠があり、モデルがタイムアウトする。
    When: 質問を送信する。
    Then: 200でfailedと安全な本文を返し、ログに例外型と継続結果を記録して秘密の例外文を除く。
    """
    published(client)

    def fail(*args):
        raise TimeoutError("秘密の質問本文")

    monkeypatch.setattr(client.app.state.runtime.engine, "generate", fail)
    response = ask(client)
    assert response.status_code == 200
    assert response.json()["status"] == "failed"
    event = next(r for r in records(caplog) if r["message_id"] == "KR_MODEL_FAILED")
    assert response.json()["answer"] in event["response"]
    assert event["context"]["exception_type"] == "TimeoutError"
    assert event["context"]["request_id"] == response.headers["x-request-id"]
    assert event["context"]["status"] is None, "途中のログでは未確定のHTTP statusを断定しない。"
    assert "秘密" not in json.dumps(event, ensure_ascii=False)


def test_OCR失敗をHTTP201の空領域として返し型付きログを残す(client, monkeypatch, caplog):
    """Given: 画像を添付できる文書があり、OCRコマンドが起動できない。
    When: 正常な画像を登録する。
    Then: 201でOCR失敗と空領域を返し、ログには起動例外の型と復旧手順を記録する。
    """
    import io

    from PIL import Image

    doc = create(client)
    data = io.BytesIO()
    Image.new("RGB", (10, 10), "white").save(data, format="PNG")

    def fail(*args, **kwargs):
        raise OSError("秘密のファイルパス")

    monkeypatch.setattr("kotorelay.operations.images.upload_image.functions.subprocess.run", fail)
    response = client.post(
        f"/api/images/documents/{doc['id']}",
        headers=headers(),
        files={"file": ("test.png", data.getvalue(), "image/png")},
    )
    assert response.status_code == 201
    assert response.json()["ocr"]["status"] == "failed" and response.json()["ocr"]["regions"] == []
    event = next(r for r in records(caplog) if r["message_id"] == "KR_OCR_FAILED")
    assert "HTTP 201" in event["response"] and "秘密" not in str(event)


@pytest.mark.parametrize(
    "error,code",
    [
        (Problem(503, "integrity", "保存不整合"), "integrity"),
        (OSError("秘密のパス"), "external_failure"),
    ],
)
def test_索引失敗のログにジョブへ保存する失敗コードを残す(error, code):
    """Given: 索引処理が業務例外または外部サービス例外で失敗する。
    When: ジョブ失敗の型付きログcontextを組み立てる。
    Then: ジョブに保存する失敗コードを記録し、生の例外文を含めない。
    """
    context = continuation_context(MessageId.INDEX_FAILED, error)
    assert context.code == code
    assert "秘密" not in context.model_dump_json()
