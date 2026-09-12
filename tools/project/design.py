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
sys.path[:0] = [str(ROOT / "backend/src"), str(ROOT / "infra/src")]
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
    return sorted(set(paths + [ROOT / "spec/requirements/requirements.json", Path(__file__)]))


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
    schema = app.openapi()
    output["OPENAPI.gen.json"] = dump(schema)
    operations = {}
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
        base = "api/" + operation_id
        docs = {kind: f"docs/design/generated/{base}.{kind}.md" for kind in KINDS}
        operations[operation_id] = docs
        rows.append(
            [method.upper(), route.path, summary, f"[{operation_id}]({base}.detail-design.md)"]
        )

        def emit(kind: str, body: str, base: str = base, summary: str = summary) -> None:
            output[f"{base}.{kind}.md"] = header + f"# {summary} — {kind}\n\n" + body

        emit(
            "interface",
            f"`{method.upper()} {route.path}`\n\n"
            + "アプリケーションが出力するOpenAPI operation。参照型と継承設定は同梱OPENAPI.gen.j"
            "sonのcomponentsで解決します。\n\n```json\n"
            + dump(operation)
            + "```\n\n"
            + table(
                ["参照型", "制約"],
                [
                    [name, json.dumps(value, ensure_ascii=False)]
                    for name, value in schema.get("components", {}).get("schemas", {}).items()
                    if "#/components/schemas/" + name in dump(operation)
                ],
            ),
        )
        tx = (
            "DBはrepeatable-read相当のtransaction。変更時に組織revisionをCAS更新し、"
            "競合は全体rollback→409。モデル呼出しはtransaction外、回答確定は別transaction"
            "で再認可。"
        )
        emit(
            "detail-design",
            f"目的: {summary}。\n\n"
            "入力はinterface帳票の型制約に従います。認可はサーバーの有効所属と権限から決まります。\n\n"
            f"{tx}\n\n## DB操作と入出力\n\n"
            + table(
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
            + "\n## 前提・正常／異常分岐\n\n"
            + table(["実装箇所", "検査条件", "不成立時／分岐", "HTTP"], factors)
            + "\n## 応答項目の取得元\n\n"
            + table(["実装箇所", "返却式（DB行・変換結果・固定値）"], returns)
            + "\n異常時: DB transactionがrollbackします。S3の内容ハッシュ実体は孤立し得るため、公開"
            "認可に使わず、保持期間後の削除処理で回収します。外部配送失敗はoutboxのerror_codeとattemp"
            "tsへ記録します。",
        )
        emit(
            "query",
            tx
            + "\n\n"
            + ("DB操作はありません。healthは固定の稼働状態を返します。\n" if not sql_names else "")
            + "\n".join(
                "## "
                + name
                + "\n\n正本: `"
                + queries[name][0].relative_to(ROOT).as_posix()
                + "`\n\n```sql\n"
                + queries[name][1].sql(dialect="postgres", pretty=True)
                + "\n```\n\n"
                + table(
                    ["入力／出力型", "定義"],
                    [
                        [ast.unparse(a), ast.unparse(a.annotation) if a.annotation else "なし"]
                        for a in inventory.nodes["kotorelay.generated.queries." + name].args.args
                    ],
                )
                + "\n戻り値: `"
                + ast.unparse(inventory.nodes["kotorelay.generated.queries." + name].returns)
                + "`\n"
                for name in sql_names
            ),
        )
        emit(
            "messages",
            table(
                ["ID", "level", "テンプレート", "条件", "出力型・マスク", "場所", "運用"],
                [
                    [
                        "KR_REQUEST",
                        "INFO",
                        LOG_MESSAGES["KR_REQUEST"],
                        "HTTP応答生成時",
                        "request_id:UUID、method:str、status:int。機密本文とJWTは記録しない。",
                        "backend/src/kotorelay/main.py:security_headers",
                        "5xxはrequest_idから処理失敗を照合。409は再読込後に再試行。",
                    ]
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
            sequence.append("        A->>D: " + name)
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
            + "\n```\n\n## 制御順序（関数内の行順）\n\n"
            + table(["関数", "行", "要素", "条件・早期終了・例外"], flow),
        )
        emit(
            "unit-test",
            "実在するpytest関数とassertから抽出。パラメータごとの実行成否は品質ポータルで確認します。共有するA"
            "PI群の境界試験も含みます。\n\n## 入力・認可・分岐要因\n\n"
            + table(["場所", "要因／要素", "異常結果", "HTTP"], factors)
            + "\n## Given / When / Then\n\n"
            + table(
                ["日本語ケース／test node", "Given", "When", "Then（期待状態）"],
                [
                    [
                        str(c["name"]) + " / " + str(c["id"]),
                        c["given"],
                        " ; ".join(c["requests"]) or "SDK境界を実行",
                        " ; ".join(c["assertions"])
                        or "pytest.raises / mock assertion で例外・依存先を検証",
                    ]
                    for c in relevant
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
        header + "# API一覧\n\n" + table(["method", "path", "目的", "6帳票の入口"], rows)
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
                "markdown": ["docs/design/generated/DATA.md"],
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
