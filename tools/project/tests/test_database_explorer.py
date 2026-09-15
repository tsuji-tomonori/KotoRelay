"""DB探索の複合参照・原文・CRUD対応を独立した入力で確認する。"""

import json
from pathlib import Path

import pytest
import sqlglot

from tools.project.database_explorer import build_database


def schema(tmp_path, statements):
    nodes, paths = {}, {}
    for name, sql in statements.items():
        path = tmp_path / f"{name}.sql"
        path.write_text(sql)
        nodes[name] = sqlglot.parse_one(sql, read="postgres")
        paths[name] = path
    return nodes, paths


def test_複合キーの対応とnullableとDDL原文を保持する(tmp_path):
    ddl, paths = schema(
        tmp_path,
        {
            "parent": "CREATE TABLE parent (tenant TEXT, id INT, PRIMARY KEY (tenant, id))",
            "child": "CREATE TABLE child (id INT PRIMARY KEY, tenant TEXT NOT NULL, parent_id INT, "
            "n INT DEFAULT 3, UNIQUE (tenant, parent_id), "
            "FOREIGN KEY (tenant, parent_id) REFERENCES parent (tenant, id))",
        },
    )
    data = build_database(ddl, paths, {}, [], tmp_path)
    columns = {c["name"]: c for c in data["tables"][0]["columns"]}
    assert columns["id"]["primaryKey"] and not columns["id"]["nullable"]
    assert not columns["tenant"]["nullable"]
    assert columns["parent_id"]["nullable"]
    assert columns["n"]["default"] == "3"
    assert data["relationships"][0]["columns"] == ["tenant", "parent_id"]
    assert data["relationships"][0]["targetColumns"] == ["tenant", "id"]
    assert data["tables"][0]["ddl"] == paths["child"].read_text()
    assert "UNIQUE (tenant, parent_id)" in data["tables"][0]["constraints"]


def test_存在しない参照先のカラムを拒否する(tmp_path):
    ddl, paths = schema(
        tmp_path,
        {
            "parent": "CREATE TABLE parent (id INT PRIMARY KEY)",
            "child": "CREATE TABLE child (id INT, FOREIGN KEY (id) REFERENCES parent (missing))",
        },
    )
    with pytest.raises(ValueError, match="外部キー列"):
        build_database(ddl, paths, {}, [], tmp_path)


def test_SQL原文と対象ごとの操作を区別して到達しないSQLも保持する(tmp_path):
    ddl, paths = schema(
        tmp_path,
        {
            "source": "CREATE TABLE source (id INT PRIMARY KEY)",
            "target": "CREATE TABLE target (id INT PRIMARY KEY)",
        },
    )
    path = tmp_path / "copy.sql"
    path.write_text(
        "-- 元テーブルから対象テーブルへコピーする。\nINSERT INTO target SELECT id FROM source"
    )
    queries = {"copy": (path, sqlglot.parse_one(path.read_text(), read="postgres"))}
    data = build_database(ddl, paths, queries, [], tmp_path)
    assert data["queries"][0]["access"] == {"source": "R", "target": "C"}
    assert data["queries"][0]["sql"] == path.read_text()
    assert data["operations"] == []
    with pytest.raises(ValueError, match="未知SQL"):
        build_database(ddl, paths, queries, [{"id": "test", "queries": ["missing"]}], tmp_path)


def test_公開DBデータのAPI集合とCRUDが既存帳票と完全一致する():
    import csv

    root = Path("docs/design/generated")
    data = json.loads((root / "DATABASE.gen.json").read_text())
    queries = {q["id"]: q for q in data["queries"]}
    operations = {op["id"]: op for op in data["operations"]}
    with (root / "crud/db.csv").open() as stream:
        rows = list(csv.DictReader(stream))
    assert len(rows) == len(operations)
    for row in rows:
        operation = operations[row.pop("api")]
        for table, expected in row.items():
            actual = "".join(
                c
                for c in "CRUD"
                if any(c in queries[q]["access"].get(table, "") for q in operation["queries"])
            )
            assert actual == expected, (operation["id"], table)
    assert {t["source"] for t in data["tables"]} == {
        p.as_posix() for p in Path("backend/migrations").glob("*.sql")
    }
    assert {q["source"] for q in data["queries"]} == {
        p.as_posix() for p in Path("backend/src").rglob("*.sql")
    }
    for t in data["tables"]:
        assert t["ddl"] == Path(t["source"]).read_text()
    for q in data["queries"]:
        assert q["sql"] == Path(q["source"]).read_text()
