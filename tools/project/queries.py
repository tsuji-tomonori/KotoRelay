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
sys.path.insert(0, str(ROOT))
APP = ROOT / "backend/src/kotorelay"
TYPES = {
    "VARCHAR": "str",
    "TEXT": "str",
    "BIGINT": "int",
    "BOOLEAN": "bool",
    "TIMESTAMPTZ": "datetime",
}


def render(sql_sources: list[Path] | None = None, *, rows: bool = True) -> str:
    from tools.project.api_documents import sql_description

    models: dict[str, tuple[str, list[tuple[str, str]]]] = {}
    sql_sources = sql_sources or []
    sources = sorted((ROOT / "backend/migrations").glob("*.sql")) + sql_sources
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
        if rows:
            lines += [f"class {cls}(BaseModel):", f'    """{table}のDDL由来の行型。"""']
            lines += [f"    {name}: {kind}" for name, kind in columns] + [""]
        else:
            lines.append(f"from kotorelay.generated.models import {cls}")
    for path in sql_sources:
        sql = path.read_text()
        description = sql_description(path)
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
                f"    {description!r}",
                f'    return db.query("{relative}", {{{values}}}, {cls})',
                "",
            ]
        elif isinstance(parsed, (exp.Insert, exp.Update)):
            lines += [
                f"def {path.stem}(db: Database, row: {cls}) -> int:",
                f"    {description!r}",
                f'    return db.execute("{relative}", row.model_dump())',
                "",
            ]
        elif isinstance(parsed, exp.Delete):
            lines += [
                f"def {path.stem}(db: Database, organization_id: str, id: str) -> int:",
                f"    {description!r}",
                f'    return db.execute("{relative}", '
                '{"organization_id": organization_id, "id": id})',
                "",
            ]
        else:
            raise ValueError(f"未対応SQL: {path}")
    return "\n".join(lines)


def formatted(source: str) -> str:
    """型生成の出力を同じRuff設定で決定的に整形する。"""
    import subprocess

    cleaned = subprocess.run(
        [
            str(Path(sys.executable).parent / "ruff"),
            "check",
            "--fix",
            "--select",
            "I,F401",
            "--stdin-filename",
            "backend/src/kotorelay/generated/queries.py",
            "-",
        ],
        input=source,
        text=True,
        capture_output=True,
        check=True,
    )
    result = subprocess.run(
        [
            str(Path(sys.executable).parent / "ruff"),
            "format",
            "--stdin-filename",
            "queries.py",
            "-",
        ],
        input=cleaned.stdout,
        text=True,
        capture_output=True,
        check=True,
    )
    return result.stdout


def build() -> dict[Path, str]:
    result = {APP / "generated/models.py": formatted(render())}
    for folder in sorted({p.parent for p in (APP / "operations").rglob("*.sql")}):
        if folder.name != "sql" or len(folder.relative_to(APP).parts) != 4:
            raise ValueError(f"APIまたは共有責務ごとのSQL配置ではありません: {folder}")
        result[folder.parent / "generated/queries.py"] = formatted(
            render(sorted(folder.glob("*.sql")), rows=False)
        )
    return result


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    output = build()
    existing = set((APP / "operations").glob("*/*/generated/queries.py"))
    stale = existing - output.keys()
    if args.check:
        if stale or any(not p.exists() or p.read_text() != body for p, body in output.items()):
            raise SystemExit("型付きquery生成物に差分または欠落があります")
    else:
        for path in stale:
            path.unlink()
        for path, body in output.items():
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(body)
    print(f"型付きSQL: {len(output) - 1}責務 / 共有DDL行型")


if __name__ == "__main__":
    main()
