"""collectorと実行原本を照合し、公開可能な品質エビデンスだけをSPAへ渡す。"""

from __future__ import annotations

import ast
import base64
import hashlib
import html
import importlib.util
import json
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

from defusedxml import ElementTree as ET

ROOT = Path(__file__).resolve().parents[2]
ART = ROOT / "artifacts"
PUBLIC = ART / "portal-public"


def read(path: Path):
    return json.loads(path.read_text())


def relative(path: str) -> str:
    return Path(path).relative_to(ROOT).as_posix() if Path(path).is_absolute() else path


def match_inventory(inventory: list[dict], results: dict[str, dict]) -> list[dict]:
    ids = [i["id"] for i in inventory]
    if len(ids) != len(set(ids)) or set(results) - set(ids):
        raise ValueError("collectorと実行原本のidentityが不一致です")
    return [
        dict(
            item, **results.get(item["id"], {"status": "not-run", "actual": "実行結果がありません"})
        )
        for item in inventory
    ]


def unit_tests() -> list[dict]:
    inventory = read(ART / "pytest-inventory.json")
    results = {}
    for case in ET.parse(ART / "pytest.xml").iter("testcase"):
        identity = case.attrib.get("classname", "") + "::" + case.attrib["name"]
        status = (
            "failed"
            if case.find("failure") is not None or case.find("error") is not None
            else "skipped"
            if case.find("skipped") is not None
            else "passed"
        )
        results[identity] = {
            "status": status,
            "actual": f"pytest: {status} / {case.attrib.get('time', '0')} 秒",
        }
    items = match_inventory(inventory, results)
    jsinventory = []
    for entry in read(ART / "vitest-inventory.json"):
        name = entry["name"].replace(" > ", " ")
        path = relative(entry["file"])
        jsinventory.append({"id": path + "::" + name, "name": name, "group": path})
    jsresults = {}
    for file in read(ART / "vitest.json")["testResults"]:
        path = relative(file["name"])
        for case in file["assertionResults"]:
            state = {"pending": "skipped", "todo": "not-run"}.get(case["status"], case["status"])
            jsresults[path + "::" + case["fullName"]] = {
                "status": state,
                "actual": f"Vitest: {state} / {case.get('duration', 0):.1f} ms",
            }
    return items + match_inventory(jsinventory, jsresults)


def specs(report: dict) -> list[dict]:
    result = []

    def visit(suite):
        result.extend(suite.get("specs", []))
        for child in suite.get("suites", []):
            visit(child)

    visit(report)
    return result


def browser_tests(
    report="playwright.json", inventory_file="playwright-inventory.json", group="Compose"
) -> list[dict]:
    inventory = []
    for spec in specs(read(ART / inventory_file)):
        for test in spec["tests"]:
            identity = test["projectName"] + "::" + spec["file"] + "::" + spec["title"]
            inventory.append(
                {
                    "id": identity,
                    "name": spec["title"],
                    "group": group + " / " + test["projectName"],
                }
            )
    results = {}
    for spec in specs(read(ART / report)):
        for test in spec["tests"]:
            identity = test["projectName"] + "::" + spec["file"] + "::" + spec["title"]
            runs = test.get("results", [])
            final = runs[-1] if runs else {}
            status = final.get("status", "not-run")
            if status == "passed" and any(r["status"] != "passed" for r in runs):
                status = "flaky"
            if status in {"timedOut", "interrupted"}:
                status = "failed"
            steps = []
            database = []
            for attachment in final.get("attachments", []):
                name = attachment["name"]
                if attachment["contentType"] == "image/png" and name.split(":")[0] in {
                    "Given",
                    "When",
                    "Then",
                }:
                    source = Path(attachment["path"])
                    if not source.resolve().is_relative_to(ART):
                        raise ValueError("公開範囲外のスクリーンショット")
                    destination = (
                        "screenshots/"
                        + hashlib.sha256(identity.encode() + name.encode()).hexdigest()
                        + ".png"
                    )
                    (PUBLIC / destination).parent.mkdir(exist_ok=True)
                    shutil.copyfile(source, PUBLIC / destination)
                    steps.append(
                        {
                            "phase": name.split(":", 1)[0],
                            "text": name.split(":", 1)[1].strip(),
                            "image": destination,
                        }
                    )
                elif attachment["contentType"] == "application/json" and name.startswith("DB状態"):
                    raw = (
                        Path(attachment["path"]).read_bytes()
                        if attachment.get("path")
                        else base64.b64decode(attachment["body"])
                    )
                    value = json.loads(raw)
                    allowed = {
                        "document_id",
                        "status",
                        "latest_version_id",
                        "version_count",
                        "submission_count",
                        "ready_chunks",
                    }
                    if not isinstance(value, dict) or set(value) - allowed:
                        raise ValueError("DB証跡は架空文書の許可された状態だけを公開します")
                    database.append(value)
            results[identity] = {
                "status": status,
                "steps": steps,
                "database": database,
                "actual": f"{status} / {final.get('duration', 0)} ms / {len(runs)}回",
            }
    return match_inventory(inventory, results)


def coverage() -> list[dict]:
    python = read(ART / "python-coverage.json")
    result = []
    for prefix, label in [("backend/", "Pythonバックエンド"), ("infra/", "Python CDK")]:
        files = {k: v for k, v in python["files"].items() if k.startswith(prefix)}
        for metric, key, covered, threshold in [
            ("lines", "num_statements", "covered_lines", 95),
            ("branches", "num_branches", "covered_branches", 90),
        ]:
            total = sum(f["summary"][key] for f in files.values())
            actual = sum(f["summary"][covered] for f in files.values())
            if total == 0:
                result.append(
                    {
                        "id": prefix + metric,
                        "name": label + " / " + metric,
                        "group": label,
                        "status": "skipped",
                        "metric": metric,
                        "tool": "coverage.py",
                        "detail": "実装に計測対象の分岐がありません（分母0、対象外）。",
                    }
                )
                continue
            result.append(
                {
                    "id": prefix + metric,
                    "name": label + " / " + ("実行可能行" if metric == "lines" else "分岐 C1相当"),
                    "group": label,
                    "status": "passed" if total and actual / total * 100 >= threshold else "failed",
                    "metric": metric,
                    "tool": "coverage.py",
                    "covered": actual,
                    "total": total,
                    "detail": f"閾値 {threshold}%。行・分岐を別々に集計します。",
                }
            )
        # 一行を複数命令へ誤変換しないようASTの実行文ノードを列挙してtrace行と対応する。
        total = actual = 0
        for path, file in files.items():
            executed = set(file["executed_lines"])
            excluded = set(file["excluded_lines"])
            for node in ast.walk(ast.parse((ROOT / path).read_text())):
                if (
                    isinstance(node, ast.stmt)
                    and not isinstance(
                        node,
                        (
                            ast.FunctionDef,
                            ast.AsyncFunctionDef,
                            ast.ClassDef,
                            ast.Global,
                            ast.Nonlocal,
                            ast.Pass,
                        ),
                    )
                    and node.lineno not in excluded
                    and not (
                        isinstance(node, ast.Expr)
                        and isinstance(node.value, ast.Constant)
                        and isinstance(node.value.value, str)
                    )
                ):
                    total += 1
                    actual += node.lineno in executed
        result.append(
            {
                "id": prefix + "statements",
                "name": label + " / 実行文 C0相当",
                "group": label,
                "status": "passed" if total and actual / total * 100 >= 95 else "failed",
                "metric": "statements",
                "tool": "Python AST + coverage.py line trace",
                "covered": actual,
                "total": total,
                "detail": "AST実行文と開始行traceを対応。CPU命令とは区別します。閾値95%。",
            }
        )
    total = read(ART / "frontend-coverage/coverage-summary.json")["total"]
    for metric, threshold in [("statements", 95), ("branches", 90), ("lines", 95)]:
        values = total[metric]
        result.append(
            {
                "id": "frontend/" + metric,
                "name": "TypeScript / "
                + {"statements": "実行文 C0相当", "branches": "分岐 C1相当", "lines": "実行可能行"}[
                    metric
                ],
                "group": "TypeScriptフロントエンド",
                "status": "passed" if values["pct"] >= threshold else "failed",
                "metric": metric,
                "tool": "Vitest / V8",
                "covered": values["covered"],
                "total": values["total"],
                "detail": f"閾値 {threshold}%。全TS/TSXアプリを対象。ポータルはE2Eで検査。",
            }
        )
    return result


def main() -> None:
    run = read(ART / "run.json")
    PUBLIC.mkdir(parents=True, exist_ok=True)
    unit = unit_tests()
    e2e = browser_tests()
    designs = []
    for path in sorted((ROOT / "docs/design/generated").rglob("*.md")):
        body = path.read_text()
        title = next(
            (line.removeprefix("# ") for line in body.splitlines() if line.startswith("# ")),
            path.stem,
        )
        designs.append(
            {
                "id": path.relative_to(ROOT).as_posix(),
                "name": title,
                "group": "API六帳票" if path.parent.name == "api" else "全体設計",
                "status": "passed",
                "body": body,
                "path": "design/index.html",
            }
        )
    for path in [
        ROOT / "docs/decisions/IMPLEMENTATION.md",
        ROOT / "docs/requirements/REQUIREMENTS.md",
        ROOT / "docs/OPERATIONS.md",
    ]:
        if path.exists():
            designs.append(
                {
                    "id": path.relative_to(ROOT).as_posix(),
                    "name": path.stem,
                    "group": "要件・設計判断・運用",
                    "status": "passed",
                    "body": path.read_text(),
                    "path": "design/index.html",
                }
            )
    (PUBLIC / "design").mkdir(exist_ok=True)
    (PUBLIC / "design/index.html").write_text(
        '<!doctype html><html lang="ja"><meta charset="utf-8"><title>生成設計</title>'
        + "".join(
            "<h1>" + html.escape(d["name"]) + "</h1><pre>" + html.escape(d["body"]) + "</pre>"
            for d in designs
        )
        + "</html>"
    )
    data = {
        "schemaVersion": 1,
        **run,
        "tests": {"applicable": True, "inventory": [i["id"] for i in unit], "items": unit},
        "e2e": {"applicable": True, "inventory": [i["id"] for i in e2e], "items": e2e},
        "static": {"applicable": True, "items": read(ART / "static.json")},
        "coverage": {"applicable": True, "items": coverage()},
        "design": {"applicable": True, "items": designs, "files": ["design/index.html"]},
    }
    (PUBLIC / "evidence.json").write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n")
    module_path = ROOT / ".agents/skills/inspect-quality-gates/scripts/evidence.py"
    spec = importlib.util.spec_from_file_location("standard_evidence", module_path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    module.validate(data, run["revision"])
    with tempfile.TemporaryDirectory(dir=ART) as temp:
        for action in ("build", "check"):
            subprocess.run(
                [
                    sys.executable,
                    str(module_path),
                    action,
                    "--manifest",
                    str(PUBLIC / "evidence.json"),
                    "--revision",
                    run["revision"],
                    "--output",
                    str(Path(temp) / "site"),
                ],
                check=True,
            )

    print(f"公開データ: 単体 {len(unit)} / E2E {len(e2e)} / 設計 {len(designs)}")


if __name__ == "__main__":
    main()
