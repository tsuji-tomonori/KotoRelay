"""router専用の宣言・戻り値・例外境界を負例で検証する。"""

import ast
from pathlib import Path
from types import SimpleNamespace

import pytest

from tools.project import api_layout, source_policy

PREFIX = "from fastapi import APIRouter\nrouter = APIRouter()\n"
BUILDER = "from example.response_builders import build_response\n"


@pytest.mark.parametrize(
    "body",
    [
        "def helper():\n    pass",
        "async def helper():\n    pass",
        "class Helper:\n    def method(self):\n        pass",
        "helper = lambda: 1",
        "@router.get('/')\ndef route():\n    def helper():\n        pass\n"
        "    return build_response()",
        "@router.get('/')\nasync def route():\n    async def helper():\n        pass\n"
        "    return build_response()",
        "@other.get('/')\ndef fake():\n    return build_response()",
        "@router.get('/')\n@router.post('/')\ndef route():\n    return build_response()",
    ],
)
def test_router内の補助関数とメソッドと偽のendpointを拒否する(body):
    with pytest.raises(ValueError, match="router|endpoint"):
        source_policy.check_source(Path("router.py"), ast.parse(PREFIX + body))


@pytest.mark.parametrize("prefix", ["", "async "])
def test_本物のendpointと関数を持たない登録routerを許可する(prefix):
    source = (
        PREFIX + BUILDER + f"@router.get('/')\n{prefix}def route():\n    return build_response()"
    )
    source_policy.check_source(Path("router.py"), ast.parse(source))
    assert source_policy.router_endpoints(Path("router.py"), ast.parse(PREFIX)) == set()


def test_APIRouterのimport別名を解決する():
    tree = ast.parse(
        "from fastapi import APIRouter as R\napi = R()\n@api.get('/')\ndef route(): pass"
    )
    assert source_policy.router_endpoints(Path("router.py"), tree) == {"route"}


@pytest.mark.parametrize(
    "caught",
    ["", " Exception", " BaseException", " (ValueError, Exception)", " builtins.Exception"],
)
def test_routerの包括的な例外捕捉を拒否する(caught):
    source = (
        PREFIX
        + BUILDER
        + "@router.get('/')\ndef route():\n    try:\n        pass\n"
        + f"    except{caught}:\n        pass\n    return build_response()"
    )
    with pytest.raises(ValueError, match="包括的"):
        source_policy.check_source(Path("router.py"), ast.parse(source))


@pytest.mark.parametrize("expression", ["{'error': 'failed'}", "None", "build_response"])
def test_endpointの応答変換の欠落を拒否する(expression):
    source = PREFIX + BUILDER + "@router.get('/')\ndef route():\n    return " + expression
    with pytest.raises(ValueError, match="応答builder"):
        source_policy.check_source(Path("router.py"), ast.parse(source))


@pytest.mark.parametrize("constant", ["True", "False"])
def test_常に同じboolを返す判定関数を拒否する(constant):
    tree = ast.parse(
        f'def is_ready() -> bool:\n    """準備済みかを判定する。"""\n    return {constant}'
    )
    with pytest.raises(ValueError, match="常に同じ"):
        source_policy.check_source(Path("functions.py"), tree)


def test_動的boolと複数のboolを返す判定を許可する():
    for body in ["return flag", "if flag:\n        return True\n    return False"]:
        tree = ast.parse(
            'def is_ready(flag) -> bool:\n    """準備済みかを判定する。"""\n    ' + body
        )
        source_policy.check_source(Path("functions.py"), tree)


def test_業務関数のHTTPException別名を拒否する():
    tree = ast.parse(
        "from fastapi import HTTPException as Error\ndef require_ready():\n"
        '    """準備状態を確認する。"""\n    raise Error(400)'
    )
    with pytest.raises(ValueError, match="共通境界"):
        source_policy.check_source(Path("functions.py"), tree)


@pytest.mark.parametrize("annotation", ["bool", "str", "bytes", "int", "list[str]"])
@pytest.mark.parametrize("statement", ["f.read()", "await f.read()"])
def test_同期と非同期の業務関数の戻り値破棄を拒否する(annotation, statement):
    inventory = call_inventory(annotation, statement)
    with pytest.raises(ValueError, match="戻り値を破棄"):
        source_policy.check_calls(inventory)


def call_inventory(annotation, statement, queries=()):
    key = "example.router.route"
    return SimpleNamespace(
        nodes={
            key: ast.parse(f"async def route():\n    {statement}").body[0],
            "example.functions.read": ast.parse(f"def read() -> {annotation}: pass").body[0],
        },
        paths={key: Path("router.py")},
        aliases={"example.router": {"f": "example.functions"}},
        reachable=lambda target: list(queries),
    )


@pytest.mark.parametrize(
    "statement", ["value = f.read()", "return f.read()", "if f.read():\n        pass"]
)
def test_結果を使用する処理と検証専用関数を許可する(statement):
    source_policy.check_calls(call_inventory("bool", statement))
    source_policy.check_calls(call_inventory("None", "f.read()"))


def test_SQL更新件数の破棄と読取結果の破棄を区別する():
    source_policy.check_calls(
        call_inventory("int", "f.read()", ["example.generated.queries.items_update"])
    )
    with pytest.raises(ValueError, match="戻り値を破棄"):
        source_policy.check_calls(
            call_inventory("int", "f.read()", ["example.generated.queries.items_get"])
        )


@pytest.mark.parametrize(
    "statement",
    [
        "import kotorelay.operations.chat.chat_history.functions as other",
        "from kotorelay.operations.chat import chat_history",
        "from ..chat_history import functions",
        "from ...chat.chat_history import functions",
    ],
)
def test_別APIへの依存をimport形式によらず拒否する(statement):
    with pytest.raises(ValueError, match="API間"):
        api_layout.check_source(
            api_layout.APP / "operations/chat/ask_question/functions.py", statement
        )


def test_未登録routerの補助関数も検査する(tmp_path):
    path = tmp_path / "operations/unused/helper/router.py"
    path.parent.mkdir(parents=True)
    path.write_text("def hidden(): pass")
    with pytest.raises(ValueError, match="endpoint以外"):
        source_policy.inspect(tmp_path, SimpleNamespace(paths={}))


def test_functionsから共有workflowへの逆依存を拒否する():
    with pytest.raises(ValueError, match="逆依存"):
        api_layout.check_source(
            api_layout.APP / "operations/indexing/shared/functions.py",
            "from .workflow import process",
        )


@pytest.mark.parametrize("body", ["pass", "if flag:\n        return build_response()"])
def test_endpointの暗黙のNone応答を拒否する(body):
    tree = ast.parse(PREFIX + BUILDER + "@router.get('/')\ndef route():\n    " + body)
    with pytest.raises(ValueError, match="応答を返さず"):
        source_policy.check_source(Path("router.py"), tree)
