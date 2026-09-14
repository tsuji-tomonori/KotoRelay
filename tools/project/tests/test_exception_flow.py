"""例外の発生位置・catchの選択・継続先をシーケンスで検証する。"""

import ast
from types import SimpleNamespace

import pytest

from tools.project.design import Inventory
from tools.project.exception_flow import UNKNOWN, known_value, matches
from tools.project.router_sequence import render


def fixture(router, functions):
    """例外の実行順を追跡する小さなAPIと呼出先を作る。"""
    nodes = {}
    for module, source in [("example.router", router), ("example.functions", functions)]:
        nodes.update((module + "." + n.name, n) for n in ast.parse(source).body)
    return SimpleNamespace(
        nodes=nodes,
        aliases={
            "example.router": {"f": "example.functions", "Problem": "kotorelay.errors.Problem"},
            "example.functions": {"Problem": "kotorelay.errors.Problem"},
        },
    )


def test_再送出する業務エラーは発生箇所で返し後続のSQLより前に終了する():
    model = fixture(
        """
def execute():
    try:
        f.reject()
        f.save()
    except Problem as exc:
        if f.unhandled(exc):
            raise
        return 'cached'
    return 'ok'
""",
        '''
def reject():
    """利用上限を確認する。"""
    raise Problem(429, 'limit', '利用上限に達しました。')
def save():
    """回答を保存する。"""
    return None
def unhandled(exc) -> bool:
    """既存回答以外の業務エラーである。"""
    return bool(exc.code != 'cached')
''',
    )
    text = "\n".join(render(model, "example.router.execute", "post", "/test", {}))
    assert text.index("利用上限を確認する。") < text.index(
        "A-->>U: HTTP 429 / 利用上限に達しました。"
    )
    assert text.index("HTTP 429") < text.index("回答を保存する。")
    assert text.count("A-->>U: HTTP 200") == 1
    assert "継続・再送出" not in text and "共通例外経路" not in text


def test_内側のcatchから再送出して外側のcatchで変換した応答をその場へ描く():
    model = fixture(
        """
def execute():
    try:
        try:
            f.reject()
        except Problem:
            raise
    except Problem:
        raise Problem(409, 'conflict', '最新の状態を確認してください。')
""",
        '''
def reject():
    """受付内容を確認する。"""
    raise Problem(403, 'forbidden', '許可されていません。')
''',
    )
    text = "\n".join(render(model, "example.router.execute", "post", "/test", {}))
    assert "HTTP 409 / 最新の状態を確認してください。" in text
    assert "HTTP 403" not in text and "HTTP 200" not in text


def test_候補を除外するcatchは採点へ進まず次の候補へ進む():
    model = Inventory()
    text = "\n".join(
        render(
            model,
            "kotorelay.operations.chat.ask_question.router.ask_question",
            "post",
            "/api/chat",
            {},
        )
    )
    chunk = text[text.index("文書断片の本文を取得") :] if "文書断片の本文を取得" in text else text
    assert "この候補の処理を終了し、次の候補へ" in chunk
    assert "失敗した処理の残りを省略し、「検索順位" not in chunk
    assert "失敗したtransactionをrollback" in text
    assert text.count("A-->>U: HTTP 200 / AnswerView") == 2


def test_SQL接続実行commitの失敗を各処理の直後に描く():
    model = Inventory()
    text = "\n".join(
        render(
            model,
            "kotorelay.operations.documents.create_document.router.create_document",
            "post",
            "/api/documents",
            {},
        )
    )
    for operation, failure in [
        ("transaction開始", "DB接続で"),
        ("文書を、所有部署", "SQL実行で"),
        ("transactionをcommit", "commitで"),
    ]:
        start = text.index(operation)
        error = text.index(failure, start)
        response = text.index("A-->>U: HTTP 409", error)
        assert start < error < response
    assert text.index("commitでDBを利用できない場合") < text.index("A-->>U: HTTP 201")
    assert "共通例外経路" not in text


def test_モデル失敗は失敗状態を設定して再認可保存へ進む():
    model = Inventory()
    text = "\n".join(
        render(
            model,
            "kotorelay.operations.chat.ask_question.router.ask_question",
            "post",
            "/api/chat",
            {},
        )
    )
    start = text.index("A->>M: generate")
    finish = text.index("モデル・検索サービスが時間切れの場合", start)
    branch = text[start:finish]
    assert "KR_MODEL_FAILED" in branch
    assert "HTTP 503" not in branch
    assert "から続ける。" in branch


def test_認証と入力形式の失敗は業務処理の前に返す():
    model = Inventory()
    text = "\n".join(
        render(
            model,
            "kotorelay.operations.chat.ask_question.router.ask_question",
            "post",
            "/api/chat",
            {},
        )
    )
    assert text.index("HTTP 401") < text.index("transaction開始")
    assert text.index("HTTP 422") < text.index("transaction開始")


def test_未解決の再送出と内部制御例外をHTTP応答として捏造しない():
    for source in [
        "def execute():\n    raise",
        "def execute():\n    raise Problem(409, 'already_answered', answer_id)",
    ]:
        model = fixture(source, "")
        with pytest.raises(ValueError):
            render(model, "example.router.execute", "get", "/test", {})


def test_未知の条件関数を実行せず未解決として返す():
    model = fixture(
        "def execute():\n    return f.check(exc)",
        """
def check(exc):
    write_external_state()
    return True
""",
    )
    value = known_value(
        model, "example.router.execute", ast.parse("f.check(exc)", mode="eval").body, {}
    )
    assert value is UNKNOWN


@pytest.mark.parametrize(
    ("declaration", "exception", "expected"),
    [
        ("Problem", "ClientError", False),
        ("(Problem, ValueError)", "ValidationError", True),
        ("OSError", "TimeoutError", True),
        ("ClientError", "Problem", False),
    ],
)
def test_例外型を区別してcatchを選ぶ(declaration, exception, expected):
    handler = ast.parse("try:\n    pass\nexcept " + declaration + ":\n    pass").body[0].handlers[0]
    assert matches(handler, exception) == expected
