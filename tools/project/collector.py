"""pytestのcollectionを実行結果と独立したinventoryとして保存する。"""

import json
from pathlib import Path


def pytest_collection_finish(session):
    items = []
    for item in session.items:
        path, name = item.nodeid.split("::", 1)
        items.append(
            {
                "id": path.removesuffix(".py").replace("/", ".") + "::" + name,
                "node": item.nodeid,
                "name": name.removeprefix("test_"),
                "group": path,
            }
        )
    output = Path("artifacts/pytest-inventory.json")
    output.parent.mkdir(exist_ok=True)
    output.write_text(json.dumps(items, ensure_ascii=False, indent=2) + "\n")
