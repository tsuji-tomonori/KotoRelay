"""API責務配置とSQLの生成境界の欠落・混在を検出する。"""

import ast
import importlib.util
from pathlib import Path

import pytest


def module(name):
    spec = importlib.util.spec_from_file_location(name, Path("tools/project") / (name + ".py"))
    value = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(value)
    return value


def test_全APIの契約とファイル責務と共有境界を検査する():
    entries = module("api_layout").inspect()
    assert len(entries) == 26
    assert len({entry["package"] for entry in entries}) == 26
    assert any(entry["sql"] for entry in entries)
    assert any(entry["shared"] for entry in entries)


@pytest.mark.parametrize(
    "source",
    [
        "from kotorelay.operations.chat.ask_question.functions import prepare",
        "def endpoint():\n    return [x for x in values]",
        "def endpoint():\n    return db.query('SELECT 1')",
    ],
)
def test_ルーターへの責務混在や別APIへの直接依存を拒否する(source):
    checker = module("api_layout")
    with pytest.raises(ValueError):
        checker.check_source(checker.APP / "operations/documents/create_document/router.py", source)


def test_型付きqueryが自分の責務のSQL正本だけを実行する():
    generator = module("queries")
    for path, body in generator.build().items():
        for call in (n for n in ast.walk(ast.parse(body)) if isinstance(n, ast.Call)):
            if isinstance(call.func, ast.Attribute) and call.func.attr in {"query", "execute"}:
                source = generator.APP / call.args[0].value
                assert source.parent == path.parent.parent / "sql"
                assert source.is_file()


@pytest.mark.parametrize("change", ["削除", "手編集", "SQL変更", "DDL変更"])
def test_型付きqueryの欠落と手編集とSQL変更を差分検査で拒否する(tmp_path, monkeypatch, change):
    generator = module("queries")
    monkeypatch.setattr(generator, "ROOT", tmp_path)
    monkeypatch.setattr(generator, "APP", tmp_path / "backend/src/kotorelay")
    ddl = tmp_path / "backend/migrations/001.sql"
    ddl.parent.mkdir(parents=True)
    ddl.write_text("CREATE TABLE items (id TEXT NOT NULL, organization_id TEXT NOT NULL)")
    sql = generator.APP / "operations/items/read_item/sql/001_items_get.sql"
    sql.parent.mkdir(parents=True)
    sql.write_text(
        "-- 現在の組織の項目を取得する。\n"
        "SELECT id, organization_id FROM items WHERE organization_id = %(organization_id)s"
    )
    monkeypatch.setattr(generator.sys, "argv", ["queries.py"])
    generator.main()
    generated = sql.parent.parent / "generated/queries.py"
    if change == "削除":
        generated.unlink()
    elif change == "手編集":
        generated.write_text(generated.read_text() + "# 手編集\n")
    elif change == "DDL変更":
        ddl.write_text(ddl.read_text().replace("id TEXT", "id BIGINT", 1))
    else:
        sql.write_text(sql.read_text() + " ORDER BY id")
    monkeypatch.setattr(generator.sys, "argv", ["queries.py", "--check"])
    with pytest.raises(SystemExit, match="差分または欠落"):
        generator.main()
