"""例外応答と日本語テスト説明の生成を正例・負例で確認する。"""

import ast

import pytest

from tools.project.design import Inventory
from tools.project.design import tests as inventory_tests
from tools.project.error_design import contracts, message_sections, problem_call
from tools.project.router_sequence import render
from tools.project.test_narrative import parse


def test_requireの既定値とキーワード引数をHTTP応答へ解決する():
    assert problem_call(ast.parse("require(ok)", mode="eval").body, require=True).status == 404
    result = problem_call(
        ast.parse("require(ok, status=403, code='forbidden')", mode="eval").body, require=True
    )
    assert result.code == "forbidden" and result.message == "この操作は許可されていません。"
    with pytest.raises(ValueError, match="静的に解決"):
        problem_call(ast.parse("Problem(status, code, message)", mode="eval").body)


def test_シーケンスに例外のstatusと本文と型付きログを表示する():
    inventory = Inventory()
    key = "kotorelay.operations.documents.save_draft.router.save_draft"
    text = "\n".join(render(inventory, key, "put", "/api/documents/{id}/draft", {}))
    for expected in [
        "HTTP 409",
        "他の操作で更新されました。",
        "KR_HTTP_REJECTED",
        "HTTP 422",
        "HTTP 503",
        "break エラー応答を返して終了",
    ]:
        assert expected in text
    assert "A-->>U: HTTP 409 / 他の操作で更新されました。" in text
    responses = [line for line in text.splitlines() if "-->>U:" in line]
    assert all("code" not in line and "request_id" not in line for line in responses)
    assert "例外を送出し通常経路を終了" not in text


def test_捕捉して継続する例外に誤ったHTTPエラーを割り当てない():
    inventory = Inventory()
    key = "kotorelay.operations.chat.ask_question.router.ask_question"
    text = "\n".join(render(inventory, key, "post", "/api/chat", {}))
    assert text.index("同じ操作IDの回答が保存されている。") < text.index(
        "A-->>U: HTTP 200 / AnswerView"
    )
    assert "A-->>U: HTTP 200 / AnswerView" in text
    assert "A-->>U: HTTP 409 / already_answered" not in text
    assert "KR_MODEL_FAILED" in text and "AnswerView.status=failed" in text
    assert "継続・再送出" not in text and "共通例外経路" not in text
    assert "捕捉した業務例外を再送出する場合" not in text
    assert "HTTP 429" in text


def test_ログ帳票を実catalogと呼出し位置と応答契約から生成する():
    inventory = Inventory()
    key = "kotorelay.operations.images.upload_image.router.upload_image"
    reached = inventory.reachable(key)
    body = "\n".join(
        message_sections(
            inventory,
            reached,
            contracts(inventory, reached, authenticated=True),
            "upload_image",
            "POST /api/images/documents/{id}",
        )
    )
    for expected in [
        "KR_OCR_FAILED",
        "OSError",
        "HTTP 201",
        "画像を読み取れません。",
        "復旧手順",
    ]:
        assert expected in body
    assert "functions.py:" in body


@pytest.mark.parametrize(
    "doc",
    [
        None,
        "Given: 前提の説明です。",
        "Given: fixture\nWhen: client.post()\nThen: x == 1",
        "Given: 前提の説明です。\nGiven: 重複した前提です。\n"
        "When: 保存を実行します。\nThen: 保存内容を確認します。",
    ],
)
def test_日本語の前提操作期待結果の欠落や重複を拒否する(doc):
    with pytest.raises(ValueError):
        parse(doc, "tests/example.py:1")


def test_テストソースから意味のある検証単位を漏れなく取り出す():
    cases = inventory_tests()
    target = next(c for c in cases if c["name"] == "競合保存は先行内容を上書きしない")
    assert target["given"] == "保存番号2の下書きがある。"
    assert "古い保存番号1" in target["when"] and "409" in target["then"]
    assert all(c["given"] and c["when"] and c["then"] for c in cases)
    assert "assertions" not in target


@pytest.mark.parametrize(
    "source",
    [
        "import logging\nlogger = logging.getLogger(__name__)",
        "logger.error('記録')",
        "ops_logger.error('unknown', context_model=ctx)",
        "ops_logger.error(MessageId.UNKNOWN, context_model=ctx)",
        "ops_logger.warning(MessageId.MODEL_FAILED, context_model=ctx)",
        "ops_logger.error(MessageId.MODEL_FAILED)",
    ],
)
def test_型付きログの迂回と未登録IDと不完全な呼出しを拒否する(tmp_path, source):
    from tools.project.error_design import validate_logging

    (tmp_path / "functions.py").write_text(source)
    with pytest.raises(ValueError):
        validate_logging(tmp_path)
