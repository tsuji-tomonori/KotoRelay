"""実コマンドを実行し、失敗を保持したまま同一runの公開入力を作る。"""

from __future__ import annotations

import argparse
import json
import os
import shlex
import shutil
import subprocess
from datetime import UTC, datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
ART = ROOT / "artifacts"
PYTHON = str(ROOT / ".venv/bin/python")
BIN = ROOT / ".venv/bin"


def execute(name: str, args: list[str], results: list[dict]) -> int:
    print(f"検証: {name}", flush=True)
    log = ROOT / ".workspace" / ("verify-" + name + ".log")
    log.parent.mkdir(exist_ok=True)
    with log.open("w") as stream:
        outcome = subprocess.run(
            args, cwd=ROOT, stdout=stream, stderr=subprocess.STDOUT, check=False
        )
    code = outcome.returncode
    if code:
        print(log.read_text()[-6000:], flush=True)
    results.append(
        {
            "id": name,
            "name": name,
            "command": shlex.join(args).replace(str(ROOT) + "/", ""),
            "status": "passed" if code == 0 else "failed",
            "detail": f"終了コード {code}。原本: .workspace/verify-{name}.log",
        }
    )
    (ART / "static.json").write_text(json.dumps(results, ensure_ascii=False, indent=2) + "\n")
    print(f"{name}: {'成功' if code == 0 else '失敗'}", flush=True)
    return code


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--report-only", action="store_true")
    args = parser.parse_args()
    ART.mkdir(exist_ok=True)
    os.environ["ASTRO_TELEMETRY_DISABLED"] = "1"
    os.environ["PYTHONPATH"] = (
        str(ROOT) + ":" + str(ROOT / "backend/src") + ":" + str(ROOT / "infra/src")
    )
    results = []
    failed = False
    if not args.report_only:
        revision = subprocess.check_output(
            [shutil.which("git") or "/usr/bin/git", "rev-parse", "HEAD"], text=True
        ).strip()
        run = {
            "revision": revision,
            "runId": os.environ.get(
                "GITHUB_RUN_ID", "local-" + datetime.now(UTC).strftime("%Y%m%dT%H%M%SZ")
            ),
            "generatedAt": datetime.now(UTC).isoformat(),
        }
        (ART / "run.json").write_text(json.dumps(run, indent=2) + "\n")
        commands = [
            ("要件生成差分", ["python3", "tools/quintflow.py", "check"]),
            ("Ruff静的解析", [str(BIN / "ruff"), "check", "backend", "infra", "tools/project"]),
            (
                "Ruff整形",
                [str(BIN / "ruff"), "format", "--check", "backend", "infra", "tools/project"],
            ),
            ("Python型検査", [str(BIN / "mypy"), "--follow-imports=silent"]),
            (
                "SQL静的解析",
                [
                    str(BIN / "sqlfluff"),
                    "lint",
                    "backend/migrations",
                    "backend/src/kotorelay/operations",
                ],
            ),
            ("型付きSQL生成差分", [PYTHON, "tools/project/queries.py", "--check"]),
            ("API責務配置", [PYTHON, "tools/project/api_layout.py"]),
            ("ESLint", ["npm", "run", "lint"]),
            ("Prettier整形", ["npm", "run", "format:check"]),
            ("TypeScript型検査", ["npm", "run", "typecheck"]),
            ("フロントビルド", ["npm", "run", "build"]),
            ("Compose起動", ["docker", "compose", "up", "-d", "--build", "--wait"]),
            (
                "Python単体結合CDK試験",
                [
                    PYTHON,
                    "-m",
                    "pytest",
                    "-p",
                    "tools.project.collector",
                    "--cov",
                    "--cov-report=json:artifacts/python-coverage.json",
                    "--junitxml=artifacts/pytest.xml",
                    "-q",
                ],
            ),
            (
                "TypeScript収集",
                [
                    "npx",
                    "vitest",
                    "list",
                    "--no-staticParse",
                    "--json=artifacts/vitest-inventory.json",
                ],
            ),
            ("TypeScript単体試験", ["npm", "test"]),
            ("E2E収集", ["npx", "playwright", "test", "--list", "--reporter=json"]),
            ("ComposeE2E", ["npx", "playwright", "test"]),
            ("設計生成差分", [PYTHON, "tools/project/design.py", "--check"]),
        ]
        for name, command in commands:
            code = execute(name, command, results)
            failed = failed or code != 0
            if name == "E2E収集" and code == 0:
                # listのJSONはstdoutへ出るため、選別して原本として保存する。
                value = (ROOT / ".workspace/verify-E2E収集.log").read_text()
                (ART / "playwright-inventory.json").write_text(value)
    else:
        results = json.loads((ART / "static.json").read_text())
        failed = any(r["status"] != "passed" for r in results)
    for name, command in [
        ("公開入力生成", [PYTHON, "tools/project/evidence.py"]),
        ("SPAビルド", ["npx", "vite", "build", "--config", "frontend/portal/vite.config.ts"]),
    ]:
        code = execute(name, command, results)
        failed = failed or code != 0
        if code:
            raise SystemExit(1)
    # coverageは行・実行文・分岐を個別に評価する。
    data = json.loads((ART / "portal-public/evidence.json").read_text())
    failed = failed or any(
        i["status"] not in {"passed", "skipped"} for i in data["coverage"]["items"]
    )
    raise SystemExit(1 if failed else 0)


if __name__ == "__main__":
    main()
