"""routerの実行順序とSQL専用モデルの契約を負例で検証する。"""

import ast
from pathlib import Path

import pytest
from pydantic import ValidationError
from test_api_layout_gates import module


def test_シーケンスはSQL名の辞書順ではなく呼出しと条件の順に生成する():
    sequence = module("router_sequence")
    inventory = module("design").Inventory()
    key = "example.router.execute"
    inventory.aliases["example.router"] = {"f": "example.functions"}
    inventory.aliases["example.functions"] = {"q": "example.generated.queries"}
    source = """
def execute(enabled):
    f.last_named_step()
    if f.is_enabled(enabled):
        f.first_named_step()
    else:
        return None
    return 'ok'
"""
    inventory.nodes[key] = ast.parse(source).body[0]
    for name, query in [("last_named_step", "z_write"), ("first_named_step", "a_read")]:
        inventory.nodes["example.functions." + name] = ast.parse(
            f"def {name}():\n    return q.{query}()"
        ).body[0]
    inventory.nodes["example.functions.is_enabled"] = ast.parse(
        'def is_enabled(enabled) -> bool:\n    """受付後の取得が有効である。"""\n    return enabled'
    ).body[0]
    descriptions = {
        "example.generated.queries.z_write": "受付記録を保存する。",
        "example.generated.queries.a_read": "受付後の記録を取得する。",
    }
    body = "\n".join(sequence.render(inventory, key, "post", "/test", descriptions))
    assert body.index("受付記録を保存する。") < body.index("alt 受付後の取得が有効である。")
    assert body.index("alt 受付後の取得が有効である。") < body.index("受付後の記録を取得する。")
    assert body.index("受付後の記録を取得する。") < body.index("else 条件不成立")
    assert "正常終了時commit" not in body


@pytest.mark.parametrize(
    "source",
    [
        "def flow(rt):\n    with rt.context('user') as ctx:\n        return ctx",
        "from kotorelay.operations.indexing.shared.router import process",
    ],
)
def test_functionsへのtransactionと全体フローの逆依存を拒否する(source):
    checker = module("api_layout")
    with pytest.raises(ValueError):
        checker.check_source(checker.APP / "operations/chat/ask_question/functions.py", source)


def test_functionsに複数更新と監査をまとめる変更を拒否する(monkeypatch):
    from tools.project import design

    inventory = design.Inventory()
    key = "kotorelay.operations.documents.create_document.functions.hidden_flow"
    inventory.nodes[key] = ast.parse(
        "def hidden_flow(ctx):\n    ctx.audit('create')\n    ctx.fence()"
    ).body[0]
    inventory.paths[key] = Path(
        "backend/src/kotorelay/operations/documents/create_document/functions.py"
    ).resolve()
    monkeypatch.setattr(design, "Inventory", lambda: inventory)
    with pytest.raises(ValueError, match="複数の更新段階"):
        module("api_layout").check_workflow_ownership()


def test_SQLの投影と束縛先から余剰列のない専用モデルを生成する(tmp_path, monkeypatch):
    generator = module("queries")
    monkeypatch.setattr(generator, "ROOT", tmp_path)
    monkeypatch.setattr(generator, "APP", tmp_path / "backend/src/kotorelay")
    ddl = tmp_path / "backend/migrations/001.sql"
    ddl.parent.mkdir(parents=True)
    ddl.write_text("CREATE TABLE items (id TEXT NOT NULL, title TEXT, revision BIGINT NOT NULL)")
    sql = generator.APP / "operations/items/read_item/sql/001_read_item.sql"
    sql.parent.mkdir(parents=True)
    sql.write_text(
        "-- 指定された識別子の表示名を取得する。\n"
        "SELECT title AS display_name FROM items WHERE id = %(target_id)s"
    )
    namespace = {}
    body = generator.formatted(generator.render([sql], rows=False))
    exec(compile(body, str(sql), "exec"), namespace)  # noqa: S102 - 固定fixtureから生成した型を検証する。
    params, row = namespace["ReadItemParams"], namespace["ReadItemRow"]
    assert set(params.model_fields) == {"target_id"}
    assert set(row.model_fields) == {"display_name"}
    assert params(target_id="item").model_dump() == {"target_id": "item"}
    assert row(display_name=None).display_name is None
    with pytest.raises(ValidationError):
        params(target_id=None)
    with pytest.raises(ValidationError):
        params(target_id="item", revision=1)
    with pytest.raises(ValidationError):
        row(display_name="表示名", id="item")
    assert body == generator.formatted(generator.render([sql], rows=False))
    sql.write_text("-- 指定された識別子の表示名を取得する。\nSELECT * FROM items")
    with pytest.raises(ValueError, match="未対応の取得式"):
        generator.render([sql], rows=False)


def test_内包表記は取得後に各要素を処理する順でシーケンスを生成する():
    sequence = module("router_sequence")
    inventory = module("design").Inventory()
    key = "example.router.execute"
    inventory.aliases["example.router"] = {"q": "example.generated.queries"}
    inventory.nodes[key] = ast.parse(
        "def execute():\n    return [q.write_item(item) for item in q.read_items()]"
    ).body[0]
    descriptions = {
        "example.generated.queries.read_items": "対象項目を一覧取得する。",
        "example.generated.queries.write_item": "取得した項目を更新する。",
    }
    body = "\n".join(sequence.render(inventory, key, "post", "/test", descriptions))
    assert body.index("対象項目を一覧取得する。") < body.index("loop q.read_items()")
    assert body.index("loop q.read_items()") < body.index("取得した項目を更新する。")


@pytest.mark.parametrize(
    ("filename", "source"),
    [
        ("router.py", "import kotorelay.operations.chat.ask_question.generated.queries as sql"),
        ("functions.py", "import kotorelay.operations.indexing.shared.router as flow"),
    ],
)
def test_import文のaliasでもSQL直接依存とフローの逆依存を拒否する(filename, source):
    checker = module("api_layout")
    with pytest.raises(ValueError):
        checker.check_source(checker.APP / "operations/chat/ask_question" / filename, source)


def test_外部呼出しのない内包表記の空の枠を図へ出さない():
    sequence = module("router_sequence")
    inventory = module("design").Inventory()
    key = "example.router.execute"
    inventory.aliases["example.router"] = {"q": "example.generated.queries"}
    inventory.nodes[key] = ast.parse(
        "def execute():\n    return [item for item in q.read_items() if item.active]"
    ).body[0]
    descriptions = {"example.generated.queries.read_items": "対象項目を一覧取得する。"}
    body = "\n".join(sequence.render(inventory, key, "get", "/test", descriptions))
    assert "対象項目を一覧取得する。" in body
    assert "loop " not in body
    assert "opt " not in body
