"""lazunexの責務検査をKotoRelayの同期APIと生成queryへ接続する。"""

from __future__ import annotations

import ast
import re
from pathlib import Path

FUNCTION = (ast.FunctionDef, ast.AsyncFunctionDef)
HTTP_METHODS = {"get", "post", "put", "patch", "delete", "head", "options", "trace", "api_route"}


def fail(path: Path, node: ast.AST, message: str) -> None:
    raise ValueError(f"{path}:{getattr(node, 'lineno', 1)}: {message}")


def imports(tree: ast.Module) -> dict[str, str]:
    """importの別名を完全修飾名へ解決する。"""
    result = {}
    for node in tree.body:
        if isinstance(node, ast.ImportFrom) and node.module:
            for alias in node.names:
                result[alias.asname or alias.name] = node.module + "." + alias.name
        elif isinstance(node, ast.Import):
            for alias in node.names:
                result[alias.asname or alias.name.split(".")[0]] = (
                    alias.name if alias.asname else alias.name.split(".")[0]
                )
    return result


def qualified(node: ast.AST, aliases: dict[str, str]) -> str:
    name = ast.unparse(node)
    first, dot, rest = name.partition(".")
    return aliases.get(first, first) + (dot + rest if dot else "")


def router_endpoints(path: Path, tree: ast.Module) -> set[str]:
    """実APIRouterの直下のendpointだけを認め、補助関数・メソッドを拒否する。"""
    aliases = imports(tree)
    routers = set()
    for node in tree.body:
        if isinstance(node, ast.Assign) and isinstance(node.value, ast.Call):
            if qualified(node.value.func, aliases) in {
                "fastapi.APIRouter",
                "fastapi.routing.APIRouter",
            }:
                routers.update(t.id for t in node.targets if isinstance(t, ast.Name))
    endpoints = set()
    for node in ast.walk(tree):
        if isinstance(node, (ast.ClassDef, ast.Lambda)):
            fail(path, node, "routerにクラス・lambdaを定義できません")
        if not isinstance(node, FUNCTION):
            continue
        decorators = [
            d
            for d in node.decorator_list
            if isinstance(d, ast.Call)
            and isinstance(d.func, ast.Attribute)
            and isinstance(d.func.value, ast.Name)
            and d.func.value.id in routers
            and d.func.attr in HTTP_METHODS
        ]
        if node not in tree.body or len(decorators) != 1:
            fail(path, node, f"routerにAPI endpoint以外の関数を定義できません: {node.name}")
        if node.name in endpoints:
            fail(path, node, f"endpoint名が重複しています: {node.name}")
        endpoints.add(node.name)
    return endpoints


def local_nodes(function: ast.AST):
    """入れ子の関数のreturnを呼出し元のreturnと混同しない。"""
    for child in ast.iter_child_nodes(function):
        if isinstance(child, (*FUNCTION, ast.ClassDef, ast.Lambda)):
            continue
        yield child
        yield from local_nodes(child)


def terminates(body: list[ast.stmt]) -> bool:
    """endpointの到達可能な末尾がreturnまたはraiseで閉じることを確認する。"""
    for node in body:
        if isinstance(node, (ast.Return, ast.Raise)):
            return True
        if isinstance(node, (ast.With, ast.AsyncWith)) and terminates(node.body):
            return True
        if isinstance(node, ast.If) and terminates(node.body) and terminates(node.orelse):
            return True
        if isinstance(node, ast.Try):
            if terminates(node.finalbody):
                return True
            if terminates(node.body + node.orelse) and all(
                terminates(h.body) for h in node.handlers
            ):
                return True
    return False


def check_source(path: Path, tree: ast.Module) -> None:
    aliases = imports(tree)
    if path.name == "router.py":
        router_endpoints(path, tree)
    for node in ast.walk(tree):
        if path.name in {"router.py", "workflow.py"} and isinstance(node, ast.ExceptHandler):
            caught = list(ast.walk(node.type)) if node.type else []
            if node.type is None or any(
                isinstance(n, (ast.Name, ast.Attribute))
                and qualified(n, aliases)
                in {"Exception", "BaseException", "builtins.Exception", "builtins.BaseException"}
                for n in caught
            ):
                fail(path, node, "APIフローの包括的な例外捕捉はできません")
        if path.name == "functions.py" and isinstance(node, ast.Call):
            if qualified(node.func, aliases) in {
                "fastapi.HTTPException",
                "starlette.exceptions.HTTPException",
            }:
                fail(path, node, "業務関数の例外はProblemで表しHTTP変換を共通境界へ委ねます")
        if not isinstance(node, FUNCTION):
            continue
        if path.name in {"functions.py", "workflow.py"}:
            if not re.search(r"[ぁ-んァ-ヶ一-龯]", ast.get_docstring(node) or ""):
                fail(path, node, f"関数の日本語の説明が欠落しています: {node.name}")
        returns = [n.value for n in local_nodes(node) if isinstance(n, ast.Return)]
        annotation = ast.unparse(node.returns).strip("'\"") if node.returns else ""
        if (
            annotation == "bool"
            and returns
            and all(
                isinstance(value, ast.Constant) and type(value.value) is bool for value in returns
            )
            and len({value.value for value in returns}) == 1
        ):
            fail(path, node, f"bool関数が常に同じ値を返しています: {node.name}")
        if path.name == "router.py":
            if not terminates(node.body):
                fail(path, node, "endpointに応答を返さず終了する経路があります")
            for value in returns:
                if not isinstance(value, ast.Call) or not qualified(value.func, aliases).endswith(
                    ".response_builders.build_response"
                ):
                    fail(path, node, "endpointは応答builderの結果を直接返す必要があります")


def check_calls(inventory) -> None:
    """実call graphと戻り型で、同期・非同期の結果の捨て忘れを検出する。"""
    from tools.project.router_sequence import resolve

    for key, path in inventory.paths.items():
        if path.name not in {"router.py", "workflow.py"}:
            continue
        for node in local_nodes(inventory.nodes[key]):
            if not isinstance(node, ast.Expr):
                continue
            call = node.value.value if isinstance(node.value, ast.Await) else node.value
            if not isinstance(call, ast.Call):
                continue
            target = resolve(inventory, key, call)
            if target not in inventory.nodes or ".functions." not in target:
                continue
            function = inventory.nodes[target]
            annotation = ast.unparse(function.returns).strip("'\"") if function.returns else ""
            if annotation in {"None", "NoReturn", "Never"}:
                continue
            # SQL更新の件数は既存DB portが返す。読取結果や判定値にはこの例外を適用しない。
            reached = inventory.reachable(target)
            queries = [name for name in reached if ".generated.queries." in name]
            if (
                annotation == "int"
                and queries
                and all(name.endswith(("_insert", "_update", "_delete")) for name in queries)
            ):
                continue
            fail(
                path,
                node,
                f"業務関数の戻り値を破棄しています: {target} -> {annotation or '型未指定'}",
            )


def inspect(app: Path, inventory) -> int:
    paths = sorted((app / "operations").rglob("*.py"))
    for path in paths:
        if "generated" not in path.parts:
            check_source(path, ast.parse(path.read_text(), filename=str(path)))
    check_calls(inventory)
    return len(paths)
