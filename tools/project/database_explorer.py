"""DDLと既存CRUD解析から、DB探索画面用の追跡可能なデータを生成する。"""

from __future__ import annotations

from pathlib import Path

from sqlglot import exp

from tools.project.api_documents import sql_access, sql_description


def build_database(ddl, ddl_sources, queries, operations, root: Path):
    """実体のない参照を拒否し、複合キーの列順とSQL原文を保持する。"""
    tables = []
    relationships = []
    for name, node in sorted(ddl.items()):
        columns = []
        primary = [c.name for key in node.find_all(exp.PrimaryKey) for c in key.expressions]
        for column in node.this.expressions:
            if not isinstance(column, exp.ColumnDef):
                continue
            constraints = column.args.get("constraints", [])
            inline_pk = any(isinstance(c.kind, exp.PrimaryKeyColumnConstraint) for c in constraints)
            if inline_pk:
                primary.append(column.name)
            default = next(
                (
                    c.kind.this.sql(dialect="postgres")
                    for c in constraints
                    if isinstance(c.kind, exp.DefaultColumnConstraint)
                ),
                None,
            )
            columns.append(
                {
                    "name": column.name,
                    "type": column.kind.sql(dialect="postgres"),
                    "nullable": not (
                        inline_pk
                        or column.name in primary
                        or any(isinstance(c.kind, exp.NotNullColumnConstraint) for c in constraints)
                    ),
                    "primaryKey": inline_pk or column.name in primary,
                    "default": default,
                    "definition": column.sql(dialect="postgres"),
                }
            )
        for index, fk in enumerate(node.find_all(exp.ForeignKey)):
            reference = fk.args["reference"].this
            target = reference.this.name
            local_columns = [c.name for c in fk.expressions]
            target_columns = [c.name for c in reference.expressions]
            if target not in ddl or len(local_columns) != len(target_columns):
                raise ValueError(f"未解決の外部キー: {name} → {target}")
            target_names = {
                c.name for c in ddl[target].this.expressions if isinstance(c, exp.ColumnDef)
            }
            if not set(target_columns) <= target_names or not set(local_columns) <= {
                c["name"] for c in columns
            }:
                raise ValueError(f"未解決の外部キー列: {name} → {target}")
            relationships.append(
                {
                    "id": f"{name}-{index}",
                    "from": name,
                    "to": target,
                    "columns": local_columns,
                    "targetColumns": target_columns,
                    "definition": fk.sql(dialect="postgres"),
                }
            )
        path = ddl_sources[name]
        tables.append(
            {
                "name": name,
                "columns": columns,
                "primaryKey": primary,
                "constraints": [
                    item.sql(dialect="postgres")
                    for item in node.this.expressions
                    if not isinstance(item, exp.ColumnDef)
                ],
                "source": path.relative_to(root).as_posix(),
                "ddl": path.read_text(),
            }
        )
    query_data = []
    for name, (path, node) in sorted(queries.items()):
        access = sql_access(node)
        if set(access) - set(ddl):
            raise ValueError(f"SQLが未知テーブルを参照: {name}")
        query_data.append(
            {
                "id": name,
                "source": path.relative_to(root).as_posix(),
                "description": sql_description(path),
                "sql": path.read_text(),
                "access": {
                    table: "".join(c for c in "CRUD" if c in actions)
                    for table, actions in sorted(access.items())
                },
            }
        )
    for operation in operations:
        if set(operation["queries"]) - set(queries):
            raise ValueError(f"APIが未知SQLを参照: {operation['id']}")
    return {
        "schemaVersion": 1,
        "tables": tables,
        "relationships": relationships,
        "queries": query_data,
        "operations": sorted(operations, key=lambda op: op["id"]),
    }


def describe_database(data):
    """公開画面の入力件数と操作仕様を、実データから設計書へ投影する。"""
    return (
        "# DBエクスプローラー\n\n"
        "品質ポータルの「DB探索」で、テーブル検索、ER図の拡大縮小・移動、"
        "テーブル選択、関連テーブルへの移動、カラム型・NULL・既定値・キー・制約・"
        "DDL原文、API別CRUDとSQL原文を確認できます。\n\n"
        f"{len(data['tables'])}テーブル、{len(data['relationships'])}外部キー、"
        f"{len(data['operations'])} API、{len(data['queries'])} SQL。\n\n"
        "入力は `DATABASE.gen.json`。DDLのSQL ASTとAPIから到達可能な型付きqueryの"
        "呼出しを使用し、CRUD帳票と同じ解析結果を共有します。"
        "外部キーは子テーブルから参照先へ向かい、複合キーは列順を保持します。"
        "DDLにない論理的な関係は推測しません。\n\n"
        "APIのCRUDは認証・共有処理・条件分岐を含む静的な和集合であり、"
        "毎回すべてのSQLが実行される意味ではありません。"
        "SQLの束縛変数をそのまま表示し、本番の実行履歴・値は取得しません。"
        "APIから到達しないSQLはテーブルのSQL一覧に残し、その旨を表示します。\n\n"
        "API名・CRUDによる絞り込み、SQLごとの全対象テーブル、API帳票への移動、"
        "同一コミットのDDL/SQLソース参照を提供します。"
        "図以外にも通常のボタンでテーブルと関係を選択でき、"
        "キーボードで拡大縮小・移動・全体表示ができます。\n"
    )
