"""API操作ごとの配置・責務・契約と依存方向を検査する。"""

from __future__ import annotations

import ast
import importlib
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path[:0] = [str(ROOT), str(ROOT / "backend/src")]
APP = ROOT / "backend/src/kotorelay"
FILES = {
    "router.py": "HTTP入力・依存注入・業務処理の順序",
    "functions.py": "API固有の業務判定・処理",
    "schemas.py": "API固有の入力制約・応答型",
    "response_builders.py": "応答型の検証・HTTP応答への変換",
    "contract.py": "operation ID・method/path・認証方式・所有先",
    "samples.py": "実HTTP試験で確認する入力と期待値",
}


def check_source(path: Path, source: str) -> None:
    """ルーターへの業務SQL・反復処理とAPI間の直接依存を拒否する。"""
    tree = ast.parse(source)
    relative = path.relative_to(APP)
    is_api = len(relative.parts) == 4 and relative.parts[0] == "operations"
    for node in ast.walk(tree):
        if isinstance(node, ast.ImportFrom) and node.module:
            parts = node.module.split(".")
            if (
                is_api
                and parts[:2] == ["kotorelay", "operations"]
                and len(parts) >= 5
                and parts[2:4] != list(relative.parts[1:3])
                and parts[3] != "shared"
            ):
                raise ValueError(f"API間の直接依存: {relative} -> {node.module}")
        if path.name == "router.py" and isinstance(
            node, (ast.For, ast.While, ast.ListComp, ast.DictComp, ast.SetComp, ast.GeneratorExp)
        ):
            raise ValueError(f"ルーターに業務反復処理があります: {relative}")
        if path.name in {"router.py", "response_builders.py", "schemas.py"}:
            if isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute):
                if node.func.attr in {"execute", "query", "transaction", "connect"}:
                    raise ValueError(f"永続化の責務が混在しています: {relative}")
        if path.name == "router.py" and isinstance(node, ast.ImportFrom):
            if node.module and ".generated.queries" in node.module:
                raise ValueError(f"ルーターがSQL境界へ直接依存しています: {relative}")


def inspect() -> list[dict[str, object]]:
    from fastapi.routing import APIRoute
    from kotorelay.main import app

    result = []
    owners = set()
    routes = list(app.routes)
    for route in routes:
        if hasattr(route, "original_router"):
            routes.extend(route.original_router.routes)
        if not isinstance(route, APIRoute):
            continue
        module = route.endpoint.__module__
        parts = module.split(".")
        if len(parts) != 5 or parts[:2] != ["kotorelay", "operations"] or parts[-1] != "router":
            raise ValueError(f"API操作単位のrouterではありません: {module}")
        owner = ".".join(parts[:-1])
        if owner in owners or parts[-2] != route.operation_id:
            raise ValueError(f"一つのAPI操作に一つのpackageが必要です: {owner}")
        owners.add(owner)
        folder = APP.joinpath(*parts[1:-1])
        for name in FILES:
            if not (folder / name).is_file():
                raise ValueError(f"APIの責務ファイルが欠落しています: {folder / name}")
        contract = importlib.import_module(owner + ".contract").CONTRACT
        if (
            contract.operation_id != route.operation_id
            or contract.path != route.path
            or {contract.method} != route.methods
            or contract.summary != route.summary
            or contract.group != parts[2]
        ):
            raise ValueError(f"API契約と実ルートが一致しません: {owner}")
        samples = importlib.import_module(owner + ".samples").SAMPLES
        if not samples or route.openapi_extra != contract.openapi_extra(samples):
            raise ValueError(f"契約・サンプルがOpenAPIへ接続されていません: {owner}")
        for name in FILES:
            check_source(folder / name, (folder / name).read_text())
        if "build_response(" not in (folder / "router.py").read_text():
            raise ValueError(f"応答組立が未接続です: {owner}")
        sql = sorted(folder.glob("sql/*.sql"))
        result.append(
            {
                "operation": route.operation_id,
                "package": folder.relative_to(ROOT).as_posix(),
                "files": dict(FILES),
                "sql": [p.relative_to(ROOT).as_posix() for p in sql],
                "queries": str(folder.relative_to(ROOT) / "generated/queries.py") if sql else None,
                "shared": sorted(
                    {
                        node.module
                        for node in ast.walk(ast.parse((folder / "functions.py").read_text()))
                        if isinstance(node, ast.ImportFrom)
                        and node.module
                        and ".shared." in node.module
                    }
                ),
            }
        )
    expected = {
        operation["operationId"]
        for path in app.openapi()["paths"].values()
        for method, operation in path.items()
        if method in {"get", "post", "put", "delete", "patch"}
    }
    if {item["operation"] for item in result} != expected or not expected:
        raise ValueError("API配置とOpenAPIのoperation集合が一致しません")
    return result


def main() -> None:
    result = inspect()
    print(f"API責務配置: {len(result)}操作の契約・所有先・応答組立・依存方向が一致")


if __name__ == "__main__":
    main()
