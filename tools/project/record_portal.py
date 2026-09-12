"""検証済みSPAへポータル自体のGWT証跡も追加し、失敗を保持する。"""

import importlib.util
import json
import shutil

from evidence import ART, PUBLIC, ROOT, browser_tests, read

items = browser_tests("portal-playwright.json", "portal-inventory.json", "Portal")
data = read(PUBLIC / "evidence.json")
data["e2e"]["items"] = [
    i for i in data["e2e"]["items"] if not i["group"].startswith("Portal")
] + items
data["e2e"]["inventory"] = [i["id"] for i in data["e2e"]["items"]]
spec = importlib.util.spec_from_file_location(
    "standard", ROOT / ".agents/skills/inspect-quality-gates/scripts/evidence.py"
)
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)
module.validate(data, data["revision"])
for target in [PUBLIC / "evidence.json", ART / "site/evidence.json"]:
    target.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n")
shutil.copytree(PUBLIC / "screenshots", ART / "site/screenshots", dirs_exist_ok=True)
print(f"ポータルE2E: {sum(i['status'] == 'passed' for i in items)} / {len(items)}")
if any(i["status"] != "passed" for i in items):
    raise SystemExit(1)
