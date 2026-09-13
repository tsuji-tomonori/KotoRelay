"""生成と公開adapterが未実行・欠落・追加を見落とさないことを検査する。"""

import importlib.util
from pathlib import Path

import pytest


def load(name):
    path = Path("tools/project") / (name + ".py")
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_collectorにある未実行ケースを成功としない():
    module = load("evidence")
    results = module.match_inventory([{"id": "a"}, {"id": "b"}], {"a": {"status": "failed"}})
    assert [r["status"] for r in results] == ["failed", "not-run"]
    with pytest.raises(ValueError):
        module.match_inventory([{"id": "a"}], {"unexpected": {"status": "passed"}})


def test_API設計の呼出し追跡がSQLまで到達する():
    module = load("design")
    reached = module.Inventory().reachable(
        "kotorelay.operations.documents.save_draft.router.save_draft"
    )
    assert any(".generated.queries.drafts_update" in name for name in reached)
    assert any(".context.Context.fence" in name for name in reached)


def test_SQLの未対応構文を型生成で拒否する(monkeypatch, tmp_path):
    module = load("queries")
    folder = tmp_path / "backend/migrations"
    folder.mkdir(parents=True)
    (folder / "001.sql").write_text("DROP TABLE example")
    monkeypatch.setattr(module, "ROOT", tmp_path)
    with pytest.raises(ValueError, match="未対応DDL"):
        module.render()


def test_分割されたTSXの画面とイベントを構文木から列挙する():
    import json
    import shutil
    import subprocess

    value = json.loads(
        subprocess.check_output(
            [shutil.which("node") or "/usr/bin/node", "tools/project/frontend-inventory.mjs"],
            text=True,
        )
    )
    components = {c["name"]: c["source"] for c in value["components"]}
    assert components["Images"] == "frontend/src/features/images/Images.tsx"
    assert components["Library"] == "frontend/src/features/documents/Library.tsx"
    assert any(
        c["event"] == "onChange" and c["source"] == components["Images"]
        for c in value["interactions"]
    )
    assert any("/documents?" in c["expression"] for c in value["calls"])
