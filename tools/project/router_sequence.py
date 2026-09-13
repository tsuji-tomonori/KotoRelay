"""routerのASTから呼出し順・分岐・反復・例外・transactionを投影する。"""

from __future__ import annotations

import ast
import re
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from tools.project.design import Inventory


def label(value: str) -> str:
    """Mermaidの制御文字を表示用の文字へ変換する。"""
    return value.replace("\n", " ").replace(";", "；").replace(":", "：").replace("#", "＃")


def resolve(inventory: Inventory, key: str, call: ast.Call) -> str:
    """実装と同じimport aliasで呼出先を解決する。"""
    module = key.rsplit(".", 1)[0]
    if module not in inventory.aliases:
        module = module.rsplit(".", 1)[0]
    name = ast.unparse(call.func)
    prefix, _, rest = name.partition(".")
    if prefix == "ctx" and rest:
        return "kotorelay.context.Context." + rest
    if prefix in {"rt", "runtime"} and rest == "context":
        return "kotorelay.runtime.Runtime.context"
    return inventory.aliases[module].get(prefix, module + "." + prefix) + (
        "." + rest if rest else ""
    )


def remove_empty_blocks(lines: list[str]) -> list[str]:
    """表示する呼出しのない枠を省き、Mermaidの空の枠の座標不定を防ぐ。"""
    frames: list[list[str]] = [[]]
    for line in lines:
        command = line.strip()
        if command.startswith(("alt ", "opt ", "loop ", "rect ", "break ")):
            frames.append([line])
        elif command == "end":
            if len(frames) == 1:
                raise ValueError("シーケンスの制御枠が対応していません")
            block = frames.pop()
            if any("->>" in item or "Note over " in item for item in block[1:]):
                frames[-1].extend([*block, line])
        else:
            frames[-1].append(line)
    if len(frames) != 1:
        raise ValueError("シーケンスの制御枠が閉じていません")
    return frames[0]


def render(
    inventory: Inventory, key: str, method: str, path: str, descriptions: dict[str, str]
) -> list[str]:
    """SQL名の集合を並べず、実際の呼出し位置でSQLの役割を表示する。"""
    from kotorelay.error_responses import DB_CONFLICT, INVALID_INPUT, UNAVAILABLE
    from kotorelay.operational_logging import CATALOG, MessageId

    from tools.project.error_design import problem_call, response_label

    catches: list[tuple[str, str]] = []
    lines = [
        "sequenceDiagram",
        "    participant U as 利用者",
        "    participant A as API router",
        "    participant F as 個別処理 functions",
        "    participant E as HTTP例外ハンドラ",
        "    participant L as 型付き運用ログ",
        "    participant D as PostgreSQLまたはDSQL",
        "    participant S as 内容ハッシュ実体",
        "    participant M as モデル・検索エンジン",
        f"    U->>A: {method.upper()} {path}",
    ]

    def add(text: str) -> None:
        lines.append("    " + text)

    def response(outcome) -> None:
        add("break エラー応答を返して終了（後続の正常処理は実行しない）")
        add("A->>E: Problemまたは依存先例外をHTTP応答へ変換・transactionはrollback")
        event = MessageId.HTTP_FAILED if outcome.status >= 500 else MessageId.HTTP_REJECTED
        add("E->>L: " + event.value + " / " + label(CATALOG[event].summary))
        add("E-->>U: " + label(response_label(outcome)))
        add("end")

    def raised(outcome) -> None:
        handler = next((place for types, place in reversed(catches) if "Problem" in types), None)
        if handler:
            add(
                "Note over A: Problemを "
                + label(handler)
                + " で捕捉 / "
                + label(response_label(outcome))
                + " は未送信。catchの継続・再送出分岐へ進む。"
            )
        else:
            response(outcome)

    def purpose(target: str) -> str:
        node = inventory.nodes[target]
        return label((ast.get_docstring(node) or node.name).splitlines()[0])

    def expression(node: ast.AST | None, current: str, stack: tuple[str, ...]) -> None:
        if node is None:
            return
        if isinstance(node, ast.IfExp):
            expression(node.test, current, stack)
            add("alt " + label(ast.unparse(node.test)))
            expression(node.body, current, stack)
            add("else 条件不成立")
            expression(node.orelse, current, stack)
            add("end")
            return
        if isinstance(node, (ast.ListComp, ast.SetComp, ast.DictComp, ast.GeneratorExp)):

            def iteration(index: int) -> None:
                if index == len(node.generators):
                    if isinstance(node, ast.DictComp):
                        expression(node.key, current, stack)
                        expression(node.value, current, stack)
                    else:
                        expression(node.elt, current, stack)
                    return
                generator = node.generators[index]
                expression(generator.iter, current, stack)
                add("loop " + label(ast.unparse(generator.iter)))
                for condition in generator.ifs:
                    expression(condition, current, stack)
                    add("opt " + label(ast.unparse(condition)))
                iteration(index + 1)
                for _ in generator.ifs:
                    add("end")
                add("end")

            iteration(0)
            return
        if isinstance(node, ast.BoolOp):
            expression(node.values[0], current, stack)
            for value in node.values[1:]:
                guarded = any(isinstance(child, ast.Call) for child in ast.walk(value))
                if guarded:
                    add("opt 前条件が" + ("成立" if isinstance(node.op, ast.And) else "不成立"))
                expression(value, current, stack)
                if guarded:
                    add("end")
            return
        if isinstance(node, ast.Call):
            target = resolve(inventory, current, node)
            if target == "kotorelay.errors.require":
                expression(
                    node.args[0]
                    if node.args
                    else next(k.value for k in node.keywords if k.arg == "condition"),
                    current,
                    stack,
                )
                condition = (
                    node.args[0]
                    if node.args
                    else next(k.value for k in node.keywords if k.arg == "condition")
                )
                add("opt 検証不成立：" + label(ast.unparse(condition)))
                raised(problem_call(node, require=True))
                add("end")
                return
            if target == "kotorelay.errors.Problem":
                return
            if ast.unparse(node.func) in {"ops_logger.error", "ops_logger.warning"}:
                event = MessageId[ast.unparse(node.args[0]).split(".")[-1]]
                add("A->>L: " + event.value + " / " + label(CATALOG[event].summary))
                add("Note over A,U: " + label(CATALOG[event].response))
                return
        for child in ast.iter_child_nodes(node):
            expression(child, current, stack)
        if not isinstance(node, ast.Call):
            return
        target = resolve(inventory, current, node)
        if target in descriptions:
            add("A->>D: " + descriptions[target])
        elif target in inventory.nodes and target not in stack:
            if target == "kotorelay.runtime.Runtime.context":
                return
            if ".router." not in target:
                add("A->>F: " + purpose(target))
            statements(inventory.nodes[target].body, target, (*stack, target))
        else:
            name = ast.unparse(node.func)
            if re.search(r"(?:ctx\.)?objects\.(get|put|delete)$", name):
                verb = name.rsplit(".", 1)[-1]
                add(
                    "A->>S: "
                    + {
                        "get": "実体を取得・ハッシュ照合",
                        "put": "実体を保存",
                        "delete": "実体を削除",
                    }[verb]
                )
            if re.search(r"(?:engine|rt\.engine)\.(generate|search|index|delete|verify)$", name):
                add("A->>M: " + name.rsplit(".", 1)[-1])

    def statements(nodes: list[ast.stmt], current: str, stack: tuple[str, ...]) -> None:
        for node in nodes:
            if isinstance(node, ast.If):
                expression(node.test, current, stack)
                add("alt " + label(ast.unparse(node.test)))
                statements(node.body, current, stack)
                if node.orelse:
                    add("else 条件不成立")
                    statements(node.orelse, current, stack)
                add("end")
            elif isinstance(node, (ast.For, ast.While)):
                condition = node.iter if isinstance(node, ast.For) else node.test
                expression(condition, current, stack)
                add("loop " + label(ast.unparse(condition)))
                statements(node.body, current, stack)
                add("end")
                statements(node.orelse, current, stack)
            elif isinstance(node, ast.Try):
                add("rect rgb(245, 247, 250)")
                add("Note over A: 例外を捕捉する処理範囲")
                handlers = [
                    (ast.unparse(h.type) if h.type else "Exception", current + ":" + str(h.lineno))
                    for h in node.handlers
                ]
                catches.extend(handlers)
                statements(node.body, current, stack)
                if handlers:
                    del catches[-len(handlers) :]
                add("end")
                for handler in node.handlers:
                    add(
                        "opt 例外発生："
                        + label(ast.unparse(handler.type) if handler.type else "例外")
                    )
                    statements(handler.body, current, stack)
                    add("end")
                if node.orelse:
                    add("opt 例外なし")
                    statements(node.orelse, current, stack)
                    add("end")
                if node.finalbody:
                    add("Note over A: 成否にかかわらず終了処理")
                    statements(node.finalbody, current, stack)
            elif isinstance(node, ast.With):
                transaction = any(
                    isinstance(item.context_expr, ast.Call)
                    and resolve(inventory, current, item.context_expr)
                    == "kotorelay.runtime.Runtime.context"
                    for item in node.items
                )
                if transaction:
                    add("rect rgb(235, 245, 255)")
                    add("Note over A,D: transaction開始・例外時rollback")
                    authentication = "kotorelay.context.Context.__init__"
                    statements(
                        inventory.nodes[authentication].body,
                        authentication,
                        (*stack, authentication),
                    )
                else:
                    for item in node.items:
                        expression(item.context_expr, current, stack)
                statements(node.body, current, stack)
                if transaction:
                    add("Note over A,D: 正常終了時commit・競合時rollback")
                    add("end")
            elif isinstance(node, ast.Return):
                expression(node.value, current, stack)
                if ".router." in current:
                    add("Note over A: この処理からreturn")
            elif isinstance(node, ast.Raise):
                if (
                    isinstance(node.exc, ast.Call)
                    and resolve(inventory, current, node.exc) == "kotorelay.errors.Problem"
                ):
                    if (
                        len(node.exc.args) > 1
                        and ast.literal_eval(node.exc.args[1]) == "already_answered"
                    ):
                        add(
                            "Note over A: already_answeredは内部制御例外。"
                            "catchで既存回答を再取得・再認可し、"
                            "HTTP 200 / AnswerView（id・answer・status・citations等）を返す。"
                            "HTTP 409は送らない。"
                        )
                    else:
                        raised(problem_call(node.exc))
                elif node.exc is None:
                    from tools.project.error_design import contracts

                    for outcome in contracts(
                        inventory, inventory.reachable(current), authenticated=False
                    ):
                        add("opt 再送出されたProblem：" + outcome.code)
                        response(outcome)
                        add("end")

                else:
                    expression(node.exc, current, stack)
                    raise ValueError(f"未対応の例外応答: {current}:{node.lineno}")
            elif isinstance(node, (ast.Break, ast.Continue)):
                add(
                    "Note over A: "
                    + ("反復を終了" if isinstance(node, ast.Break) else "次の反復へ")
                )
            elif isinstance(node, (ast.Assign, ast.AnnAssign, ast.Expr, ast.AugAssign)):
                expression(node.value, current, stack)
            elif isinstance(node, (ast.Pass, ast.Assert)):
                if isinstance(node, ast.Assert):
                    expression(node.test, current, stack)
            else:
                raise ValueError(
                    f"シーケンス未対応の構文: {current}:{node.lineno}: {type(node).__name__}"
                )

    uses_context = any(
        argument.annotation and ast.unparse(argument.annotation) == "Ctx"
        for argument in inventory.nodes[key].args.args
    )
    if uses_context:
        add("Note over A,D: 依存注入でtransaction開始・組織と所属を確認")
        authentication = "kotorelay.context.Context.__init__"
        statements(inventory.nodes[authentication].body, authentication, (key, authentication))
    statements(inventory.nodes[key].body, key, (key,))
    if uses_context:
        add("Note over A,D: 成功応答前に依存transactionをcommit・失敗時rollback")
    status = 200
    for decorator in inventory.nodes[key].decorator_list:
        if isinstance(decorator, ast.Call):
            for keyword in decorator.keywords:
                if keyword.arg == "status_code":
                    status = ast.literal_eval(keyword.value)
    annotation = inventory.nodes[key].returns
    add(f"A-->>U: HTTP {status} / " + label(ast.unparse(annotation) if annotation else "成功応答"))
    if uses_context or any(
        a.annotation and ast.unparse(a.annotation) == "Rt" for a in inventory.nodes[key].args.args
    ):
        add("Note over A,U: 共通例外経路（成功後に実行する追加処理ではない）")
        for title, outcome in [
            ("入力検証の失敗（RequestValidationError）", INVALID_INPUT),
            ("SQL実行またはcommitの競合（psycopg.Error）", DB_CONFLICT),
            ("DB接続・外部サービスの失敗（捕捉して継続する場合を除く）", UNAVAILABLE),
        ]:
            add("opt " + title)
            response(outcome)
            add("end")
    return remove_empty_blocks(lines)
