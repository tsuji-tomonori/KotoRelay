"""例外の型と既知の属性を使い、catchの実際の分岐を静的に選択する。"""

from __future__ import annotations

import ast

UNKNOWN = object()


def matches(handler: ast.ExceptHandler, exception: str) -> bool:
    """catchの宣言順を保つため、単一handlerへの型の適合だけを判定する。"""
    if handler.type is None:
        return True
    declared = handler.type.elts if isinstance(handler.type, ast.Tuple) else [handler.type]
    parents = {exception, "Exception", "BaseException"}
    if exception in {"TimeoutError", "FileNotFoundError", "UnidentifiedImageError"}:
        parents.add("OSError")
    if exception == "ValidationError":
        parents.add("ValueError")
    return any(ast.unparse(node).rsplit(".", 1)[-1] in parents for node in declared)


def known_value(inventory, key: str, node: ast.AST, bindings: dict, seen=()):
    """既知の例外属性の比較と単純な述語だけを解釈し、実装コードは実行しない。"""
    from tools.project.router_sequence import resolve

    if isinstance(node, ast.Constant):
        return node.value
    if isinstance(node, ast.Name):
        return bindings.get(node.id, UNKNOWN)
    if isinstance(node, ast.Attribute):
        owner = known_value(inventory, key, node.value, bindings, seen)
        return owner.get(node.attr, UNKNOWN) if isinstance(owner, dict) else UNKNOWN
    if isinstance(node, ast.UnaryOp) and isinstance(node.op, ast.Not):
        value = known_value(inventory, key, node.operand, bindings, seen)
        return not value if value is not UNKNOWN else UNKNOWN
    if isinstance(node, ast.Compare) and len(node.ops) == 1:
        left = known_value(inventory, key, node.left, bindings, seen)
        right = known_value(inventory, key, node.comparators[0], bindings, seen)
        if left is not UNKNOWN and right is not UNKNOWN:
            if isinstance(node.ops[0], ast.Eq):
                return left == right
            if isinstance(node.ops[0], ast.NotEq):
                return left != right
    if isinstance(node, ast.Call):
        values = [known_value(inventory, key, arg, bindings, seen) for arg in node.args]
        if ast.unparse(node.func) == "bool" and len(values) == 1:
            return bool(values[0]) if values[0] is not UNKNOWN else UNKNOWN
        target = resolve(inventory, key, node)
        function = inventory.nodes.get(target)
        if function and target not in seen:
            body = [
                n
                for n in function.body
                if not (
                    isinstance(n, ast.Expr)
                    and isinstance(n.value, ast.Constant)
                    and isinstance(n.value.value, str)
                )
            ]
            if len(body) == 1 and isinstance(body[0], ast.Return):
                arguments = dict(zip((a.arg for a in function.args.args), values, strict=False))
                arguments.update(
                    (k.arg, known_value(inventory, key, k.value, bindings, seen))
                    for k in node.keywords
                    if k.arg
                )
                return known_value(inventory, target, body[0].value, arguments, (*seen, target))
    return UNKNOWN


def exits_scope(nodes: list[ast.stmt]) -> bool:
    """returnと再送出に加え、反復の中断もcatch後へ進まない終端として扱う。"""
    for node in nodes:
        if isinstance(node, (ast.Return, ast.Raise, ast.Break, ast.Continue)):
            return True
        if isinstance(node, ast.If) and exits_scope(node.body) and exits_scope(node.orelse):
            return True
        if isinstance(node, ast.With) and exits_scope(node.body):
            return True
    return False
