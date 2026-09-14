"""条件の日本語説明とbool関数の境界を正例・負例で固定する。"""

import ast
from pathlib import Path
from types import SimpleNamespace

import pytest

from tools.project.condition_labels import describe, inspect


def inventory(
    condition,
    declaration=(
        'def allowed(value) -> bool:\n    """利用者が操作を実行できる。"""\n    return bool(value)'
    ),
    filename="router.py",
):
    """実アプリに依存せずimport aliasと条件の構文を組み立てる。"""
    key = "example." + filename.removesuffix(".py") + ".execute"
    return SimpleNamespace(
        nodes={
            key: ast.parse(
                "def execute(value):\n    if " + condition + ":\n        return value"
            ).body[0],
            "example.functions.allowed": ast.parse(declaration).body[0],
        },
        aliases={
            "example.functions": {},
            key.rsplit(".", 1)[0]: {
                "f": "example.functions",
                "allowed": "example.functions.allowed",
            },
        },
        paths={key: Path(filename)},
    ), key


@pytest.mark.parametrize("filename", ["router.py", "workflow.py"])
@pytest.mark.parametrize(
    "condition",
    [
        "f.allowed(value)",
        "allowed(value)",
        "not f.allowed(value)",
        "f.allowed(value) and not allowed(value)",
    ],
)
def test_日本語docstringを条件に使い否定と短絡の意味を保つ(filename, condition):
    model, key = inventory(condition, filename=filename)
    inspect(model)
    text = describe(model, key, model.nodes[key].body[0].test, functions_only=True)
    assert "利用者が操作を実行できる。" in text
    assert "allowed" not in text and "value" not in text
    assert ("不成立" in text) == ("not" in condition)
    assert ("かつ" in text) == ("and" in condition)


@pytest.mark.parametrize(
    "condition", ["value", "value == 1", "bool(value)", "f.allowed(value) is True", "lambda: True"]
)
def test_routerに直接書いた条件式やlambdaを拒否する(condition):
    model, _ = inventory(condition)
    with pytest.raises(ValueError, match="日本語説明を持つbool関数"):
        inspect(model)


@pytest.mark.parametrize(
    "declaration",
    [
        'def allowed(value) -> int:\n    """権限がある。"""\n    return value',
        'def allowed(value):\n    """権限がある。"""\n    return bool(value)',
        "def allowed(value) -> bool:\n    return bool(value)",
        'def allowed(value) -> bool:\n    """Check permission."""\n    return bool(value)',
    ],
)
def test_bool型または日本語説明のない条件関数を拒否する(declaration):
    model, _ = inventory("f.allowed(value)", declaration)
    with pytest.raises(ValueError, match="日本語説明を持つbool関数"):
        inspect(model)


@pytest.mark.parametrize(
    "body",
    [
        "return value if value else None",
        "while value:\n        break",
        "return next(x for x in value if x.active)",
    ],
)
def test_三項式while内包表記でも直接条件式を見逃さない(body):
    model, key = inventory("f.allowed(value)")
    model.nodes[key] = ast.parse("def execute(value):\n    " + body).body[0]
    with pytest.raises(ValueError, match="日本語説明を持つbool関数"):
        inspect(model)


def test_docstringの変更だけで図の条件説明も更新される():
    from tools.project.router_sequence import render

    model, key = inventory("f.allowed(value)")
    before = "\n".join(render(model, key, "get", "/test", {}))
    model.nodes["example.functions.allowed"].body[
        0
    ].value.value = "利用者が最新の所属で操作できる。"
    after = "\n".join(render(model, key, "get", "/test", {}))
    assert "alt 利用者が操作を実行できる。" in before
    assert "alt 利用者が最新の所属で操作できる。" in after
    assert "alt 利用者が操作を実行できる。" not in after


def test_functions以外のbool関数をrouter条件にできない():
    model, key = inventory("f.allowed(value)")
    model.aliases[key.rsplit(".", 1)[0]]["f"] = "example.helpers"
    model.nodes["example.helpers.allowed"] = model.nodes.pop("example.functions.allowed")
    with pytest.raises(ValueError, match="日本語説明を持つbool関数"):
        inspect(model)
