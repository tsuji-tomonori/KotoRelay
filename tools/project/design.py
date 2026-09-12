"""実装のAST、OpenAPI、SQL AST、合成テンプレートから現在設計を生成する。"""

from __future__ import annotations

import argparse
import ast
import hashlib
import json
import re
import shutil
import subprocess
import sys
from pathlib import Path

import sqlglot
from sqlglot import exp

ROOT = Path(__file__).resolve().parents[2]
sys.path[:0] = [str(ROOT), str(ROOT / "backend/src"), str(ROOT / "infra/src")]
OUT = ROOT / "docs/design/generated"
KINDS = ["detail-design", "interface", "messages", "query", "sequence", "unit-test"]


def dump(value: object) -> str:
    return json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n"


def table(headers: list[str], rows: list[list[object]]) -> str:
    def cell(value: object) -> str:
        return str(value).replace("|", "&#124;").replace("\n", "<br>")

    return (
        "\n".join(
            ["| " + " | ".join(headers) + " |", "| " + " | ".join(["---"] * len(headers)) + " |"]
            + ["| " + " | ".join(map(cell, row)) + " |" for row in rows]
        )
        + "\n"
    )


def sources() -> list[Path]:
    paths = []
    for folder, suffix in [
        ("backend/src", ".py"),
        ("backend/src", ".sql"),
        ("backend/tests", ".py"),
        ("backend/migrations", ".sql"),
        ("infra/src", ".py"),
        ("infra/tests", ".py"),
        ("frontend/src", ".tsx"),
        ("frontend/src", ".ts"),
        ("frontend/src", ".astro"),
        ("frontend/src", ".css"),
        ("frontend/portal", ".tsx"),
        ("frontend/portal", ".ts"),
        ("frontend/portal", ".css"),
        ("frontend/tests", ".tsx"),
        ("frontend/tests", ".ts"),
        ("e2e", ".ts"),
    ]:
        paths.extend((ROOT / folder).rglob("*" + suffix))
    return sorted(
        set(
            paths
            + [
                ROOT / "spec/requirements/requirements.json",
                Path(__file__),
                ROOT / "tools/project/api_documents.py",
            ]
        )
    )


class Inventory:
    def __init__(self) -> None:
        self.nodes: dict[str, ast.FunctionDef | ast.AsyncFunctionDef] = {}
        self.paths: dict[str, Path] = {}
        self.aliases: dict[str, dict[str, str]] = {}
        for path in (ROOT / "backend/src").rglob("*.py"):
            module = ".".join(path.relative_to(ROOT / "backend/src").with_suffix("").parts)
            tree = ast.parse(path.read_text())
            aliases = {}
            for node in tree.body:
                if isinstance(node, ast.ImportFrom) and node.module:
                    for alias in node.names:
                        aliases[alias.asname or alias.name] = node.module + "." + alias.name
                if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                    self.nodes[module + "." + node.name] = node
                    self.paths[module + "." + node.name] = path
                if isinstance(node, ast.ClassDef):
                    for child in node.body:
                        if isinstance(child, (ast.FunctionDef, ast.AsyncFunctionDef)):
                            self.nodes[module + "." + node.name + "." + child.name] = child
                            self.paths[module + "." + node.name + "." + child.name] = path
            self.aliases[module] = aliases

    def reachable(self, initial: str) -> list[str]:
        seen: set[str] = set()
        pending = [initial]
        while pending:
            key = pending.pop(0)
            if key in seen:
                continue
            seen.add(key)
            node = self.nodes[key]
            module = ".".join(
                self.paths[key].relative_to(ROOT / "backend/src").with_suffix("").parts
            )
            for call in [n for n in ast.walk(node) if isinstance(n, ast.Call)]:
                name = ast.unparse(call.func)
                prefix, _, rest = name.partition(".")
                target = self.aliases[module].get(prefix, module + "." + prefix) + (
                    "." + rest if rest else ""
                )
                if prefix == "ctx" and rest:
                    target = "kotorelay.context.Context." + rest
                if prefix in {"rt", "runtime"} and rest == "context":
                    target = "kotorelay.runtime.Runtime.context"
                if target in self.nodes and target not in seen:
                    pending.append(target)
        return sorted(seen)


def tests() -> list[dict[str, object]]:
    result = []
    for path in sorted((ROOT / "backend/tests").glob("test*.py")):
        tree = ast.parse(path.read_text())
        helpers = {n.name: n for n in tree.body if isinstance(n, ast.FunctionDef)}
        for name, node in helpers.items():
            if not name.startswith("test_"):
                continue
            expanded = [node]
            seen = {name}
            for current in expanded:
                for call in ast.walk(current):
                    if (
                        isinstance(call, ast.Call)
                        and isinstance(call.func, ast.Name)
                        and call.func.id in helpers
                        and call.func.id not in seen
                    ):
                        seen.add(call.func.id)
                        expanded.append(helpers[call.func.id])
            calls = [
                n for current in expanded for n in ast.walk(current) if isinstance(n, ast.Call)
            ]
            requests = [
                ast.unparse(n)
                for n in calls
                if isinstance(n.func, ast.Attribute)
                and n.func.attr in {"get", "post", "put"}
                and ast.unparse(n.func.value) == "client"
            ]
            assertions = [ast.unparse(n.test) for n in ast.walk(node) if isinstance(n, ast.Assert)]
            result.append(
                {
                    "id": path.relative_to(ROOT).as_posix() + "::" + name,
                    "name": name.removeprefix("test_"),
                    "requests": requests,
                    "given": ", ".join(node.args.args[i].arg for i in range(len(node.args.args)))
                    or "モジュールの固定fixture",
                    "assertions": assertions,
                    "helpers": sorted(seen),
                }
            )
    return result


def synth() -> dict[str, object]:
    from aws_cdk import App, Aspects
    from aws_cdk.assertions import Template
    from cdk_nag import AwsSolutionsChecks
    from kotorelay_infra.stack import KotoRelayStack

    app = App(outdir=str(ROOT / "artifacts/design-synth"))
    stack = KotoRelayStack(app, "KotoRelay")
    Aspects.of(app).add(AwsSolutionsChecks(verbose=True))
    app.synth()
    template = Template.from_stack(stack).to_json()
    # CDKのDockerアセットハッシュは配布対象コードの変化を反映し、絶対パスは除く。
    for resource in template["Resources"].values():
        resource.pop("Metadata", None)
    return template


def build() -> tuple[dict[str, str], dict[str, object]]:
    from fastapi.routing import APIRoute
    from kotorelay.main import LOG_MESSAGES, app

    from tools.project import api_documents as layout

    files = sources()
    hashes = {
        p.relative_to(ROOT).as_posix(): hashlib.sha256(p.read_bytes()).hexdigest() for p in files
    }
    digest = hashlib.sha256(dump(hashes).encode()).hexdigest()
    header = f"<!-- 実装から生成。直接編集しない。入力SHA256: {digest} -->\n\n"
    output: dict[str, str] = {}
    inventory = Inventory()
    cases = tests()
    queries = {}
    descriptions = {}
    ddl = {}
    for path in sorted((ROOT / "backend/migrations").glob("*.sql")):
        node = sqlglot.parse_one(path.read_text(), read="postgres")
        if not isinstance(node, exp.Create) or not isinstance(node.this, exp.Schema):
            raise ValueError(f"未対応DDL: {path}")
        ddl[node.this.this.name] = node
    for path in sorted((ROOT / "backend/src").rglob("*.sql")):
        node = sqlglot.parse_one(re.sub(r"%\((\w+)\)s", r":\1", path.read_text()), read="postgres")
        if not isinstance(node, (exp.Select, exp.Insert, exp.Update, exp.Delete)):
            raise ValueError(f"未対応SQL: {path}")
        queries[path.stem] = (path, node)
        descriptions[path.stem] = layout.sql_description(path)
    schema = app.openapi()
    output["OPENAPI.gen.json"] = dump(schema)
    operations = {}
    groups = {}
    matrices = {"db": {}, "objects": {}, "vectors": {}}
    crud_evidence = []
    rows = []
    routes = list(app.routes)
    for route in routes:
        if hasattr(route, "original_router"):
            routes.extend(route.original_router.routes)
        if not isinstance(route, APIRoute):
            continue
        operation_id = route.operation_id
        if not operation_id:
            raise ValueError(f"operationId欠落: {route.path}")
        method = sorted(route.methods)[0].lower()
        operation = schema["paths"][route.path][method]
        key = route.endpoint.__module__ + "." + route.endpoint.__name__
        reached = inventory.reachable(key)
        # 認証依存とHTTP middlewareを全APIへ合成する。healthだけは認証不要。
        if operation_id != "health":
            reached = sorted(
                set(reached + inventory.reachable("kotorelay.context.Context.__init__"))
            )
        sql_names = sorted(
            {k.rsplit(".", 1)[-1] for k in reached if k.startswith("kotorelay.generated.queries.")}
        )
        factors = []
        returns = []
        for k in reached:
            node = inventory.nodes[k]
            source = inventory.paths[k].relative_to(ROOT).as_posix()
            for n in ast.walk(node):
                if isinstance(n, ast.Call) and ast.unparse(n.func) == "require":
                    factors.append(
                        [
                            f"{source}:{n.lineno}",
                            ast.unparse(n.args[0]),
                            ast.unparse(n.args[1]) if len(n.args) > 1 else "not_found",
                            ast.unparse(n.args[2]) if len(n.args) > 2 else "404",
                        ]
                    )
                if isinstance(n, ast.If):
                    factors.append(
                        [
                            f"{source}:{n.lineno}",
                            ast.unparse(n.test),
                            "then / else の実装分岐",
                            "制御フロー参照",
                        ]
                    )
                if isinstance(n, ast.Return):
                    returns.append(
                        [f"{source}:{n.lineno}", ast.unparse(n.value) if n.value else "None"]
                    )
        segment = route.path.split("/")[2]
        relevant = [c for c in cases if any("/api/" + segment in str(r) for r in c["requests"])]
        if not relevant:
            relevant = [c for c in cases if "DB" in str(c["name"]) or "認証" in str(c["name"])]
        summary = operation.get("summary", operation_id)
        base = f"api/{segment}/{operation_id}"
        docs = {kind: f"docs/design/generated/{base}/{kind}.md" for kind in KINDS}
        operations[operation_id] = docs
        entry = [method.upper(), route.path, summary, f"[{operation_id}]({base}/README.md)"]
        rows.append(entry)
        groups.setdefault(segment, []).append((operation_id, summary))
        output[f"{base}/README.md"] = (
            header
            + f"# {summary} ({operation_id})\n\n`{method.upper()} {route.path}`\n\n"
            + "\n".join(f"- [{label}]({kind}.md)" for kind, label in layout.LABELS.items())
        )
        for matrix in matrices.values():
            matrix[operation_id] = {}
        for name in sql_names:
            for resource, actions in layout.sql_access(queries[name][1]).items():
                if resource not in ddl:
                    raise ValueError(f"CRUDの未知テーブル: {resource}")
                matrices["db"][operation_id].setdefault(resource, set()).update(actions)
                crud_evidence.append(
                    [
                        operation_id,
                        "DB",
                        resource,
                        "".join(k for k in "CRUD" if k in actions),
                        queries[name][0].relative_to(ROOT).as_posix(),
                    ]
                )
        object_calls = {"put": "CU", "get": "R", "delete": "D"}
        vector_calls = {"index": "CU", "search": "R", "verify": "R", "delete": "D"}
        for key_name in reached:
            for call in (n for n in ast.walk(inventory.nodes[key_name]) if isinstance(n, ast.Call)):
                name = ast.unparse(call.func)
                for prefix, methods, store, resource in [
                    ("ctx.objects.", object_calls, "objects", "content_object"),
                    ("engine.", vector_calls, "vectors", "vector"),
                    ("rt.engine.", vector_calls, "vectors", "vector"),
                ]:
                    if name.startswith(prefix) and name[len(prefix) :] in methods:
                        action = methods[name[len(prefix) :]]
                        matrices[store][operation_id].setdefault(resource, set()).update(action)
                        crud_evidence.append(
                            [
                                operation_id,
                                store,
                                resource,
                                action,
                                f"{inventory.paths[key_name].relative_to(ROOT)}:{call.lineno}",
                            ]
                        )

        def emit(
            kind: str,
            body: str,
            base: str = base,
            summary: str = summary,
            query_names: tuple[str, ...] = tuple(queries[name][0].name for name in sql_names),
        ) -> None:
            layout.validate(kind, body, list(query_names))
            output[f"{base}/{kind}.md"] = (
                header
                + f"# {summary} — {layout.LABELS[kind]}\n\n"
                + f"章構成: [lazunex API帳票]({layout.REFERENCE}/40.apis)。\n\n"
                + body
            )

        emit("interface", layout.interface(operation, schema))
        tx = (
            "DBはrepeatable-read相当のtransaction。変更時に組織revisionをCAS更新し、"
            "競合は全体rollback→409。モデル呼出しはtransaction外、回答確定は別transaction"
            "で再認可。"
        )
        input_text = "\n\n".join(
            f"**{name}**\n\n{body}"
            for name, body in zip(
                layout.CHAPTERS["interface"][:4],
                layout.input_sections(operation, schema),
                strict=True,
            )
        )
        changes = (
            table(
                ["query", "DB対象", "処理"],
                [
                    [
                        name,
                        ", ".join(t.name for t in queries[name][1].find_all(exp.Table)),
                        queries[name][1].key.upper(),
                    ]
                    for name in sql_names
                ],
            )
            if sql_names
            else "DBへのアクセスはありません。"
        )
        emit(
            "detail-design",
            layout.sections(
                "detail-design",
                [
                    f"目的: {summary}。\n\n" + input_text,
                    "認証・認可と型制約を満たすこと。以下は実装の検査条件と制御分岐です。条件の成立を一律に正常系とは扱いません。\n\n"
                    + table(["実装箇所", "検査条件", "不成立時／分岐", "HTTP"], factors),
                    tx
                    + "\n\n参照操作も併記します。SELECTは変更ではありません。\n\n"
                    + changes
                    + "\n異常時はDB transactionがrollbackします。内容ハッシュ実体は孤立し得るため、"
                    "公開認可には使いません。配送失敗はoutboxへ記録します。",
                    layout.response_section(operation, schema)
                    + "\n\n**応答項目の取得元**\n\n"
                    + table(["実装箇所", "返却式（DB行・変換結果・固定値）"], returns),
                ],
            ),
        )
        query_bodies = []
        for name in sql_names:
            path, sql_node = queries[name]
            function = inventory.nodes["kotorelay.generated.queries." + name]
            argument_rows = [
                [a.arg, ast.unparse(a.annotation) if a.annotation else "なし"]
                for a in function.args.args
                if a.arg != "db"
            ]
            conditions = [
                n.sql(dialect="postgres")
                for n in sql_node.walk()
                if isinstance(n, (exp.Where, exp.Join, exp.Order, exp.Limit))
            ]
            contents = [
                sql_node.key.upper(),
                descriptions[name],
                table(
                    ["DB", "テーブル", "CRUD"],
                    [
                        ["PostgreSQL / DSQL", target, "".join(k for k in "CRUD" if k in actions)]
                        for target, actions in layout.sql_access(sql_node).items()
                    ],
                ),
                table(["引数", "型"], argument_rows) if argument_rows else "引数はありません。",
                f"型: `{ast.unparse(function.returns)}`",
                "\n\n".join(conditions) or "SQL内にWHERE/JOIN/ORDER/LIMIT条件はありません。",
            ]
            query_bodies.append(
                "## "
                + path.name
                + "\n\n正本: `"
                + path.relative_to(ROOT).as_posix()
                + "`\n\n"
                + "\n\n".join(
                    f"### {heading}\n\n{body}"
                    for heading, body in zip(layout.QUERY_SECTIONS, contents, strict=True)
                )
                + "\n\n```sql\n"
                + sql_node.sql(dialect="postgres", pretty=True)
                + "\n```"
            )
        emit(
            "query",
            tx
            + "\n\n"
            + (
                "\n\n".join(query_bodies)
                or "DB操作はありません。このAPIは固定の稼働状態を返します。"
            ),
        )
        emit(
            "messages",
            layout.sections(
                "messages",
                [
                    table(
                        ["項目", "値"],
                        [
                            ["operation", operation_id],
                            ["endpoint", f"{method.upper()} {route.path}"],
                            ["router", inventory.paths[key].relative_to(ROOT).as_posix()],
                        ],
                    ),
                    "共通HTTP middlewareのlogger呼出しと実行時LOG_MESSAGESを読み取ります。"
                    "HTTPエラーメッセージをログとして置換しません。",
                    table(
                        ["id", "message_id", "ログ概要"],
                        [["M001", "KR_REQUEST", "HTTP応答時の相関ID・メソッド・ステータス"]],
                    ),
                    "### `M001` `KR_REQUEST`\n\n"
                    + table(
                        ["項目", "内容"],
                        [
                            ["level", "INFO"],
                            ["テンプレート", LOG_MESSAGES["KR_REQUEST"]],
                            ["条件", "HTTP応答生成時"],
                            ["場所", "backend/src/kotorelay/main.py:security_headers"],
                            ["運用対応", "5xxはrequest_idから照合。409は再読込後に再試行。"],
                        ],
                    )
                    + "\n#### 出力項目\n\n"
                    + table(
                        ["出力項目", "型", "マスク規則"],
                        [
                            ["request_id", "UUID文字列", "相関用ID"],
                            ["method", "str", "HTTPメソッドのみ"],
                            ["status", "int", "HTTPコードのみ"],
                        ],
                    ),
                    "LOG_MESSAGESとlogger呼出しが実装に存在すること。本文・JWT・OCR本文をログに含めないこと。lazunex固有のloggerラッパーやWARNING以上の運用規則は、本実装の規則として転記しません。",
                ],
            ),
        )
        sequence = [
            "sequenceDiagram",
            "    participant U as 利用者",
            "    participant A as API",
            "    participant D as PostgreSQLまたはDSQL",
            "    participant S as S3実体",
            "    participant M as Bedrock",
            f"    U->>A: {method.upper()} {route.path}",
            "    A->>D: 有効組織・所属を取得",
            "    alt 認可条件が不成立",
            "        A-->>U: 401または403または404",
            "    else 許可",
        ]
        for name in sql_names:
            sequence.append("        A->>D: " + descriptions[name])
        if segment in {"documents", "images", "chat", "operations", "reviews"}:
            sequence += [
                "        A->>S: 内容ハッシュ実体を照合",
                "        opt 実体欠落・ハッシュ不一致",
                "            A-->>U: 利用不可・回答保留",
                "        end",
            ]
        if segment in {"chat", "operations"}:
            sequence += [
                "        opt 有効根拠または索引配送",
                "            A->>M: 上限付きモデル実行",
                "            alt 外部サービス失敗",
                "                M-->>A: 例外",
                "                A->>D: 失敗状態を記録",
                "            else 成功",
                "                M-->>A: 結果",
                "            end",
                "        end",
            ]
        sequence += [
            "        A->>D: 必要な変更を確定（競合時rollback）",
            "        A-->>U: 認可済み結果",
            "    end",
        ]
        if operation_id == "health":
            sequence = [
                "sequenceDiagram",
                "    participant U as 利用者",
                "    participant A as API",
                f"    U->>A: {method.upper()} {route.path}",
                "    A-->>U: 固定の稼働状態",
            ]
        # 詳細な条件とtry/except順序はASTから再生成し、概略図に続けて掲載する。
        flow = []
        for k in reached:
            if ".generated." in k:
                continue
            for n in sorted(ast.walk(inventory.nodes[k]), key=lambda n: getattr(n, "lineno", 0)):
                if isinstance(
                    n, (ast.If, ast.For, ast.Try, ast.ExceptHandler, ast.Return, ast.Raise)
                ):
                    expr = (
                        ast.unparse(n.test)
                        if isinstance(n, ast.If)
                        else ast.unparse(n.type)
                        if isinstance(n, ast.ExceptHandler) and n.type
                        else ast.unparse(n.value)
                        if isinstance(n, ast.Return) and n.value
                        else type(n).__name__
                    )
                    flow.append([k, n.lineno, type(n).__name__, expr])
        emit(
            "sequence",
            "```mermaid\n"
            + "\n".join(sequence)
            + "\n```\n\n**制御順序（関数内の行順）**\n\n"
            + table(["関数", "行", "要素", "条件・早期終了・例外"], flow),
        )
        factor_details = (
            "\n\n".join(
                f"### F{i:02d} 条件分岐\n\n対象: `{f[0]}`。式: `{f[1]}`\n\n"
                + table(
                    ["要素ID", "要素", "期待観点"],
                    [
                        [
                            f"F{i:02d}-true",
                            "成立",
                            "成立側の実装を実行。正常／異常は上記式と処理に依存する。",
                        ],
                        [f"F{i:02d}-false", "不成立", f"{f[2]} / {f[3]}"],
                    ],
                )
                for i, f in enumerate(factors, 1)
            )
            or "明示的な条件分岐はありません。"
        )
        case_rows = [[f"TC{i:03d}", c["name"], c["id"]] for i, c in enumerate(relevant, 1)]
        case_details = "\n\n".join(
            f"### TC{i:03d}\n\n"
            + table(
                ["項目", "内容"],
                [
                    ["日本語ケース", c["name"]],
                    ["test node", c["id"]],
                    ["Given", c["given"]],
                    ["When", " ; ".join(c["requests"]) or "SDK境界を実行"],
                    [
                        "Then",
                        " ; ".join(c["assertions"])
                        or "pytest.raises / mock assertionで例外・依存先を検証",
                    ],
                ],
            )
            for i, c in enumerate(relevant, 1)
        )
        emit(
            "unit-test",
            layout.sections(
                "unit-test",
                [
                    "FastAPI/Pydanticの入力検証、認証依存、共通middlewareを適用します。healthは認証不要です。型制約違反は422、認証失敗は401、commit競合は409です。",
                    factor_details,
                    "参照先と同じ章名を保持しています。ここでは実在するテストを列挙します。要因の完全な直積や到達不能条件の自動証明は実装していないため、全組合せの網羅を示す表ではありません。API群に共通する境界試験を含みます。\n\n"
                    + table(["Case ID", "日本語ケース", "test node"], case_rows),
                    case_details or "このAPI群に対応する実在ケースがありません。",
                ],
            ),
        )
    expected_operations = {
        operation["operationId"]
        for path in schema["paths"].values()
        for method, operation in path.items()
        if method in {"get", "post", "put", "delete", "patch"}
    }
    if set(operations) != expected_operations:
        raise ValueError("OpenAPIとASTのoperation集合が一致しません")
    output["API.md"] = (
        header
        + "# API一覧\n\n## APIグループ\n\n"
        + "\n".join(f"- [{group}](api/{group}/README.md)" for group in groups)
        + "\n\n## API一覧\n\n"
        + table(["method", "path", "目的", "6帳票の入口"], rows)
    )
    for group, entries in groups.items():
        output[f"api/{group}/README.md"] = (
            header
            + f"# APIグループ: {group}\n\n"
            + "\n".join(f"- [{summary} ({op})]({op}/README.md)" for op, summary in entries)
        )
    for kind, matrix in matrices.items():
        resources = (
            sorted(ddl)
            if kind == "db"
            else sorted({resource for cells in matrix.values() for resource in cells})
        )
        csv_body = layout.csv_matrix(matrix, resources)
        output[f"crud/{kind}.csv"] = csv_body
        title = {
            "db": "DB CRUD対応表",
            "objects": "オブジェクト保存 CRUD対応表",
            "vectors": "ベクトル索引 CRUD対応表",
        }[kind]
        matrix_rows = [
            [
                op,
                *[
                    "".join(c for c in "CRUD" if c in cells.get(resource, set())) or "—"
                    for resource in resources
                ],
            ]
            for op, cells in sorted(matrix.items())
        ]
        diagrams = []
        for group, entries in groups.items():
            lines = ["flowchart LR"]
            edges = 0
            for index, (op, _) in enumerate(entries):
                for j, resource in enumerate(resources):
                    actions = "".join(c for c in "CRUD" if c in matrix[op].get(resource, set()))
                    if actions:
                        lines.append(f'    A{index}["{op}"] -->|{actions}| R{j}["{resource}"]')
                        edges += 1
            diagrams.append(
                f"## APIグループ: {group}\n\n"
                + (
                    "```mermaid\n" + "\n".join(lines) + "\n```"
                    if edges
                    else "この保存先へのアクセスはありません。"
                )
            )
        evidence_rows = [row for row in crud_evidence if row[1] == ("DB" if kind == "db" else kind)]
        output[f"crud/{kind}.md"] = (
            header + f"# {title}\n\n[参照構成]({layout.REFERENCE}/30.crud)。"
            "C=作成、R=参照、U=更新、D=削除。条件分岐を含む到達可能な呼出しの静的な和集合です。"
            "全操作が毎回実行される意味ではありません。S3のputとvectorのindexは上書きを含むため"
            "CUとします。Bedrockの生成呼出しはCRUDに含めません。\n\n"
            + table(["API", *resources], matrix_rows)
            + "\n"
            + "\n\n".join(diagrams)
            + "\n\n## 抽出根拠\n\n"
            + table(["API", "保存先", "リソース", "CRUD", "SQL正本／呼出箇所"], evidence_rows)
        )
    output["crud/README.md"] = (
        header
        + "# CRUD図と対応表\n\n"
        + "\n".join(
            f"- [{label}]({kind}.md)（[CSV]({kind}.csv)）"
            for kind, label in [
                ("db", "DB"),
                ("objects", "オブジェクト保存"),
                ("vectors", "ベクトル索引"),
            ]
        )
    )
    data_rows = []
    er = ["erDiagram"]
    for name, node in ddl.items():
        body = []
        for item in node.this.expressions:
            body.append([item.key, item.sql(dialect="postgres")])
            if isinstance(item, exp.ForeignKey):
                ref = item.args["reference"].this.this.name
                er.append(f"    {ref} ||--o{{ {name} : references")
        crud = [
            [qname, qnode.key.upper()]
            for qname, (_, qnode) in queries.items()
            if name in {t.name for t in qnode.find_all(exp.Table)}
        ]
        data_rows += [
            f"## {name}\n\n"
            + table(["属性・制約", "DDL"], body)
            + "\n"
            + table(["access pattern", "操作"], crud)
        ]
    output["DATA.md"] = (
        header
        + "# 実装データモデル\n\n"
        + f"{len(ddl)}テーブル。manifest/evidence/OCRを検証付きJSONとして固定します。"
        "企画段階の33テーブル案を統合しました。複合参照制約とAPI認可で保護します。\n\n```mermaid\n"
        + "\n".join(er)
        + "\n```\n\n"
        + "\n".join(data_rows)
    )
    template = synth()
    output["TEMPLATE.gen.json"] = dump(template)
    resources = template["Resources"]
    output["INFRA.md"] = (
        header + "# AWS実装構成\n\nPython CDKをsynthしたCloudFormationに基づきます。AWSへの"
        "実デプロイと実DSQL/Bedrock疎通は別の運用検証です。\n\n"
        + table(
            ["logical ID", "種別", "設定・IAM・参照関係"],
            [[name, r["Type"], dump(r.get("Properties", {}))] for name, r in resources.items()],
        )
        + "\n## 出力\n\n"
        + table(
            ["名前", "値"], [[name, dump(v)] for name, v in template.get("Outputs", {}).items()]
        )
        + "\n## 費用と運用\n\nNAT/ALB/OCU/CMKを作成しません。Lambda、"
        "S3、S3 Vectors、DSQL、Bedrock、ログ、配信は利用量・保存量に応じて課金されます。Even"
        "tBridgeが15分間隔でoutboxを配送します。S3/DSQLは削除保護・Retainです。cdk-na"
        "g例外理由はstack.pyの各resourceに限定して保持します。"
    )
    frontend = json.loads(
        subprocess.check_output(
            [shutil.which("node") or "/usr/bin/node", "tools/project/frontend-inventory.mjs"],
            cwd=ROOT,
            text=True,
        )
    )
    output["FRONTEND.md"] = (
        header + "# フロントエンド\n\nAstroの単一ルート `/` がReactワークスペースを起動します。"
        "TypeScript構文木から全TS/TSXのコンポーネント・呼出し・操作イベントを列挙します。\n\n"
        + table(
            ["コンポーネント", "実装", "行"],
            [[c["name"], c["source"], c["line"]] for c in frontend["components"]],
        )
        + "\n## API呼出しと状態遷移\n\n"
        + table(
            ["実装", "行", "処理"],
            [[c["source"], c["line"], c["expression"]] for c in frontend["calls"]],
        )
        + "\n## 操作イベント\n\n"
        + table(
            ["実装", "行", "イベント", "処理"],
            [
                [c["source"], c["line"], c["event"], c["expression"]]
                for c in frontend["interactions"]
            ],
        )
        + "\n## スタイル定義\n\n```css\n"
        + (ROOT / "frontend/src/styles/tokens.css").read_text()
        + "\n```\n"
        + "\n## 表示と版の整合\n\n同じPlacedDocumentをプレビュー・審査・閲覧に使います。"
        "挿入位置はUnicodeコードポイント数です。OCR領域の識別と位置を独立して保持し、"
        "版と画像は認可付きAPIから読み込みます。未保存確認はWorkspaceで共有し、"
        "引用版の変更と非許可状態を区別して表示します。詳細は上記の実装イベントに対応します。"
    )
    output["manifest.json"] = dump(
        {
            "source_sha256": hashes,
            "layout_reference": layout.REFERENCE,
            "operation_documents": operations,
            "sql": sorted(queries),
            "tests": [c["id"] for c in cases],
        }
    )

    def markdown(prefix):
        return [
            f"docs/design/generated/{p}"
            for p in output
            if p.endswith(".md") and (p.startswith(prefix) if prefix else True)
        ]

    command = [".venv/bin/python", "tools/project/design.py"]
    contract = {
        "schema_version": 1,
        "surfaces": {
            "api": {
                "status": "required",
                "sources": ["backend/src"],
                "markdown": markdown("api/") + ["docs/design/generated/API.md"],
                "generate": command,
                "check": command + ["--check"],
                "openapi": "docs/design/generated/OPENAPI.gen.json",
                "operation_documents": operations,
            },
            "data": {
                "status": "required",
                "sources": ["backend/migrations"],
                "markdown": ["docs/design/generated/DATA.md"] + markdown("crud/"),
                "generate": command,
                "check": command + ["--check"],
            },
            "infra": {
                "status": "required",
                "sources": ["infra/src"],
                "markdown": ["docs/design/generated/INFRA.md"],
                "generate": command,
                "check": command + ["--check"],
            },
            "frontend": {
                "status": "required",
                "sources": ["frontend/src"],
                "markdown": ["docs/design/generated/FRONTEND.md"],
                "generate": command,
                "check": command + ["--check"],
            },
        },
    }
    return output, contract


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    output, contract = build()
    actual = (
        {p.relative_to(OUT).as_posix(): p.read_text() for p in OUT.rglob("*") if p.is_file()}
        if OUT.exists()
        else {}
    )
    contract_path = ROOT / ".dev-standard/design.json"
    if args.check:
        if (
            actual != output
            or not contract_path.exists()
            or contract_path.read_text() != dump(contract)
        ):
            raise SystemExit("現在設計に欠落またはdriftがあります")
    else:
        for relative, value in output.items():
            path = OUT / relative
            if path.is_symlink() or any(parent.is_symlink() for parent in path.parents):
                raise ValueError("symlink出力は拒否します")
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(value)
        for stale in set(actual) - set(output):
            (OUT / stale).unlink()
        contract_path.write_text(dump(contract))
    count = len(contract["surfaces"]["api"]["operation_documents"])
    print(f"設計: {len(output)} artifacts / API {count} operations")


if __name__ == "__main__":
    main()
