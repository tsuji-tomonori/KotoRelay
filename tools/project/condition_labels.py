"""bool述語の日本語説明を条件ラベルの唯一の入力として解決する。"""

from __future__ import annotations

import ast
import re


def describe(inventory, key: str, node: ast.AST, *, functions_only: bool = False) -> str:
    """否定と短絡条件を保持し、説明のない式や非bool関数を拒否する。"""
    from tools.project.router_sequence import resolve

    if isinstance(node, ast.UnaryOp) and isinstance(node.op, ast.Not):
        return (
            "不成立：（"
            + describe(inventory, key, node.operand, functions_only=functions_only)
            + "）"
        )
    if isinstance(node, ast.BoolOp):
        separator = " かつ " if isinstance(node.op, ast.And) else " または "
        return separator.join(
            "（" + describe(inventory, key, value, functions_only=functions_only) + "）"
            for value in node.values
        )
    if isinstance(node, ast.Call):
        target = resolve(inventory, key, node)
        function = inventory.nodes.get(target)
        if (
            function is not None
            and function.returns is not None
            and ast.unparse(function.returns).strip("'\"") == "bool"
            and (not functions_only or ".functions." in target)
        ):
            summary = (ast.get_docstring(function) or "").splitlines()
            if summary and re.search(r"[ぁ-んァ-ヶ一-龯]", summary[0]):
                return summary[0]
    raise ValueError(
        f"条件は日本語説明を持つbool関数が必要です: {key}:{node.lineno}: {ast.unparse(node)}"
    )


def inspect(inventory) -> None:
    """APIフローのif・三項式・while・generator条件を漏れなく検査する。"""
    for key, path in inventory.paths.items():
        if path.name not in {"router.py", "workflow.py"}:
            continue
        for node in ast.walk(inventory.nodes[key]):
            if isinstance(node, (ast.If, ast.IfExp, ast.While)):
                describe(inventory, key, node.test, functions_only=True)
            if isinstance(node, ast.comprehension):
                for condition in node.ifs:
                    describe(inventory, key, condition, functions_only=True)
