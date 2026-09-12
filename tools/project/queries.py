"""DDLとSQL ASTから型付き行・query wrapperを決定的に生成する。"""

from __future__ import annotations

import argparse
import hashlib
import re
import sys
from pathlib import Path

import sqlglot
from sqlglot import exp

ROOT = Path(__file__).resolve().parents[2]
APP = ROOT / "backend/src/kotorelay"
TYPES = {
    "VARCHAR": "str",
    "TEXT": "str",
    "BIGINT": "int",
    "BOOLEAN": "bool",
    "TIMESTAMPTZ": "datetime",
}


def render() -> str:
    models: dict[str, tuple[str, list[tuple[str, str]]]] = {}
    sources = sorted((ROOT / "backend/migrations").glob("*.sql")) + sorted(
        (APP / "operations").rglob("*.sql")
    )
    digest = hashlib.sha256(b"".join(p.read_bytes() for p in sources)).hexdigest()
    lines = [
        f'"""DDL・SQLから生成した型付き境界。直接編集しない。\nSHA256: {digest}\n"""',
        "from datetime import datetime",
        "from pydantic import BaseModel",
        "from kotorelay.db import Database",
        "",
    ]
    for path in sorted((ROOT / "backend/migrations").glob("*.sql")):
        node = sqlglot.parse_one(path.read_text(), read="postgres")
        if not isinstance(node, exp.Create) or not isinstance(node.this, exp.Schema):
            raise ValueError(f"未対応DDL: {path}")
        table = node.this.this.name
        columns: list[tuple[str, str]] = []
        for column in node.this.expressions:
            if isinstance(column, exp.ColumnDef):
                kind = column.args["kind"].sql(dialect="postgres").split("(")[0].upper()
                nullable = not any(
                    isinstance(c.kind, exp.NotNullColumnConstraint) for c in column.constraints
                )
                columns.append((column.name, TYPES[kind] + (" | None" if nullable else "")))
        cls = "".join(s.title() for s in table.split("_")) + "Row"
        models[table] = cls, columns
        lines += [f"class {cls}(BaseModel):", f'    """{table}のDDL由来の行型。"""']
        lines += [f"    {name}: {kind}" for name, kind in columns] + [""]
    for path in sorted((APP / "operations").rglob("*.sql")):
        sql = path.read_text()
        parsed = sqlglot.parse_one(re.sub(r"%\((\w+)\)s", r":\1", sql), read="postgres")
        tables = {t.name for t in parsed.find_all(exp.Table)}
        if len(tables) != 1:
            raise ValueError(f"未対応の複数テーブルquery: {path}")
        table = tables.pop()
        cls, cols = models[table]
        params = list(dict.fromkeys(re.findall(r"%\((\w+)\)s", sql)))
        if set(params) - dict(cols).keys():
            raise ValueError(f"DDLにない引数: {path}")
        relative = path.relative_to(APP).as_posix()
        if isinstance(parsed, exp.Select):
            declarations = ", ".join(f"{p}: {dict(cols)[p]}" for p in params)
            values = ", ".join(f'"{p}": {p}' for p in params)
            lines += [
                f"def {path.stem}(db: Database, {declarations}) -> list[{cls}]:",
                f'    """{table}を認証組織の範囲で取得する。"""',
                f'    return db.query("{relative}", {{{values}}}, {cls})',
                "",
            ]
        elif isinstance(parsed, (exp.Insert, exp.Update)):
            lines += [
                f"def {path.stem}(db: Database, row: {cls}) -> int:",
                f'    """{table}の型検査済み行を保存する。"""',
                f'    return db.execute("{relative}", row.model_dump())',
                "",
            ]
        elif isinstance(parsed, exp.Delete):
            lines += [
                f"def {path.stem}(db: Database, organization_id: str, id: str) -> int:",
                f'    """{table}の指定行だけを削除する。"""',
                f'    return db.execute("{relative}", {{"organization_id": organization_id, "id": id}})',
                "",
            ]
        else:
            raise ValueError(f"未対応SQL: {path}")
    return "\n".join(lines)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    import subprocess

    result = subprocess.run(
        [
            str(Path(sys.executable).parent / "ruff"),
            "format",
            "--stdin-filename",
            "queries.py",
            "-",
        ],
        input=render(),
        text=True,
        capture_output=True,
        check=True,
    )
    path = APP / "generated/queries.py"
    if args.check:
        if not path.exists() or path.read_text() != result.stdout:
            raise SystemExit("型付きquery生成物に差分または欠落があります")
    else:
        path.parent.mkdir(exist_ok=True)
        path.write_text(result.stdout)


if __name__ == "__main__":
    main()
