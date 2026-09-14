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
    if prefix == "self" and ".Context." in key and rest:
        return "kotorelay.context.Context." + rest
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
    from kotorelay.error_responses import DB_CONFLICT, INVALID_INPUT, UNAVAILABLE, ErrorOutcome
    from kotorelay.errors import MESSAGES
    from kotorelay.operational_logging import CATALOG, MessageId

    from tools.project.condition_labels import describe
    from tools.project.error_design import problem_call, response_label
    from tools.project.exception_flow import UNKNOWN, exits_scope, known_value, matches
    from tools.project.source_policy import terminates

    status = 200
    for decorator in inventory.nodes[key].decorator_list:
        if isinstance(decorator, ast.Call):
            for keyword in decorator.keywords:
                if keyword.arg == "status_code":
                    status = ast.literal_eval(keyword.value)
    annotation = inventory.nodes[key].returns
    success_label = f"HTTP {status} / " + label(
        ast.unparse(annotation) if annotation else "成功応答"
    )
    active_transactions = 0
    deferred_conditions: dict[str, tuple[str, ast.AST]] = {}
    catches: list[tuple[list[ast.ExceptHandler], str, tuple[str, ...], str, int]] = []
    caught: list[tuple[str, object, dict, ast.ExceptHandler]] = []
    lines = [
        "sequenceDiagram",
        "    participant U as 利用者",
        "    participant A as API router",
        "    participant F as 個別処理 functions",
        "    participant L as 型付き運用ログ",
        "    participant D as PostgreSQLまたはDSQL",
        "    participant S as 内容ハッシュ実体",
        "    participant M as モデル・検索エンジン",
        f"    U->>A: {method.upper()} {path}",
    ]

    def add(text: str) -> None:
        lines.append("    " + text)

    def condition_text(node: ast.AST, current: str) -> str:
        token = f"条件参照{len(deferred_conditions)}番"
        deferred_conditions[token] = (current, node)
        return token

    def success() -> None:
        add("break 応答を返して終了")
        if uses_context or active_transactions:
            commit()
        add("A-->>U: " + success_label)
        add("end")

    def response(outcome) -> None:
        add("break エラー応答を返して終了")
        event = MessageId.HTTP_FAILED if outcome.status >= 500 else MessageId.HTTP_REJECTED
        add("A->>L: " + event.value)
        add("A-->>U: " + label(response_label(outcome)))
        add("end")

    def raised(outcome, exception="Problem") -> None:
        nonlocal active_transactions
        for index in range(len(catches) - 1, -1, -1):
            handlers, owner, stack, resume, depth = catches[index]
            handler = next((h for h in handlers if matches(h, exception)), None)
            if handler is None:
                continue
            suspended = catches[index:]
            del catches[index:]
            attributes = outcome.model_dump() if outcome else {}
            caught.append((exception, outcome, {handler.name: attributes}, handler))
            previous_depth = active_transactions
            if active_transactions > depth:
                add("A->>D: 失敗したtransactionをrollback")
            active_transactions = depth
            try:
                statements(handler.body, owner, stack, resume)
                if not exits_scope(handler.body):
                    add("Note over A: 失敗した処理の残りを省略し、" + resume)
            finally:
                caught.pop()
                active_transactions = previous_depth
                catches.extend(suspended)
            return
        if outcome is None or outcome.code == "already_answered":
            raise ValueError(f"HTTP応答を解決できない例外: {exception}")
        response(outcome)

    def failure(title, outcome, exception="Problem") -> None:
        add("opt " + title)
        raised(outcome, exception)
        add("end")

    def database_failure(stage: str) -> None:
        failure(stage + "で競合が発生した場合", DB_CONFLICT, "Error")
        failure(stage + "でDBを利用できない場合", UNAVAILABLE, "Error")

    def commit() -> None:
        add("A->>D: transactionをcommit")
        database_failure("commit")

    def purpose(target: str) -> str:
        node = inventory.nodes[target]
        return label((ast.get_docstring(node) or node.name).splitlines()[0])

    def expression(node: ast.AST | None, current: str, stack: tuple[str, ...]) -> None:
        if node is None:
            return
        if isinstance(node, ast.IfExp):
            expression(node.test, current, stack)
            add("alt " + condition_text(node.test, current))
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
                    add("opt " + condition_text(condition, current))
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
                add("opt 検証不成立：" + purpose(current))
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
        if target in descriptions or (
            ".generated.queries." in target and target in inventory.nodes
        ):
            add("A->>D: " + (descriptions[target] if target in descriptions else purpose(target)))
            database_failure("SQL実行")
        elif target in inventory.nodes and target not in stack:
            if target == "kotorelay.runtime.Runtime.context":
                return
            if not any(part in target for part in (".router.", ".workflow.")):
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
                if verb == "get":
                    failure(
                        "実体の欠落・ハッシュ不一致の場合",
                        ErrorOutcome(status=503, code="integrity", message=MESSAGES["integrity"]),
                    )
                failure("実体の入出力が失敗した場合", UNAVAILABLE, "OSError")
                failure("実体サービスが失敗した場合", UNAVAILABLE, "ClientError")
            if re.search(r"(?:engine|rt\.engine)\.(generate|search|index|delete|verify)$", name):
                add("A->>M: " + name.rsplit(".", 1)[-1])
                failure("モデル・検索サービスが失敗した場合", UNAVAILABLE, "ClientError")
                failure("モデル・検索サービスが時間切れの場合", UNAVAILABLE, "TimeoutError")
            if target == "subprocess.run":
                add("A->>M: OCRを実行する")
                failure("OCRの起動・実行が失敗した場合", UNAVAILABLE, "OSError")
                failure("OCRが時間切れの場合", None, "TimeoutExpired")
                failure("OCRが異常終了した場合", None, "CalledProcessError")
            if target in {"PIL.Image.open", "PIL.ImageOps.exif_transpose"} or name in {
                "source.verify",
                "image.save",
            }:
                add("A->>F: 画像を読み取り・検証・変換する")
                failure("画像の読取・変換が失敗した場合", UNAVAILABLE, "UnidentifiedImageError")
            if name.endswith(".model_validate_json") and any(
                any(matches(h, "ValidationError") for h in handlers)
                for handlers, _, _, _, _ in catches
            ):
                failure("保存データの形式が不正な場合", None, "ValidationError")

    def continuation(nodes: list[ast.stmt], current: str, fallback: str) -> str:
        if nodes:
            calls = [n for n in ast.walk(nodes[0]) if isinstance(n, ast.Call)]
            target = next(
                (
                    resolve(inventory, current, n)
                    for n in calls
                    if resolve(inventory, current, n) in inventory.nodes
                    and resolve(inventory, current, n) != "kotorelay.runtime.Runtime.context"
                ),
                None,
            )
            if target:
                return "「" + purpose(target) + "」から続ける。"
        return fallback

    def statements(
        nodes: list[ast.stmt],
        current: str,
        stack: tuple[str, ...],
        resume_at: str = "呼出し元の後続処理を続ける。",
    ) -> None:
        nonlocal active_transactions
        for position, node in enumerate(nodes):
            next_resume = continuation(nodes[position + 1 :], current, resume_at)
            if isinstance(node, ast.If):
                value = (
                    known_value(inventory, current, node.test, caught[-1][2]) if caught else UNKNOWN
                )
                if value is not UNKNOWN:
                    selected = node.body if value else node.orelse
                    statements(selected, current, stack, next_resume)
                    if terminates(selected):
                        return
                    continue
                expression(node.test, current, stack)
                add("alt " + condition_text(node.test, current))
                statements(node.body, current, stack, next_resume)
                if node.orelse:
                    add("else 条件不成立")
                    statements(node.orelse, current, stack, next_resume)
                add("end")
            elif isinstance(node, (ast.For, ast.While)):
                condition = node.iter if isinstance(node, ast.For) else node.test
                expression(condition, current, stack)
                add(
                    "loop "
                    + (
                        label(ast.unparse(condition))
                        if isinstance(node, ast.For)
                        else condition_text(condition, current)
                    )
                )
                statements(node.body, current, stack, next_resume)
                add("end")
                statements(node.orelse, current, stack, next_resume)
            elif isinstance(node, ast.Try):
                add("rect rgb(245, 247, 250)")
                add("Note over A: 例外を捕捉する処理範囲")
                resume = next_resume
                catches.append((node.handlers, current, stack, resume, active_transactions))
                statements(node.body, current, stack, next_resume)
                catches.pop()
                add("end")
                if node.orelse:
                    add("opt 例外なし")
                    statements(node.orelse, current, stack, next_resume)
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
                    active_transactions += 1
                    add("rect rgb(235, 245, 255)")
                    add("A->>D: transaction開始")
                    database_failure("DB接続")
                    authentication = "kotorelay.context.Context.__init__"
                    statements(
                        inventory.nodes[authentication].body,
                        authentication,
                        (*stack, authentication),
                    )
                else:
                    for item in node.items:
                        expression(item.context_expr, current, stack)
                statements(node.body, current, stack, next_resume)
                if transaction:
                    active_transactions -= 1
                    if not terminates(node.body):
                        commit()
                    add("end")
            elif isinstance(node, ast.Return):
                expression(node.value, current, stack)
                if current == key:
                    success()
                elif ".workflow." in current:
                    add("Note over A: 共有処理を終了して呼出し元へ結果を返す")
                elif caught and node in ast.walk(caught[-1][3]):
                    add("Note over F,A: 失敗結果を呼出し元へ返し、この個別処理を終了する")
            elif isinstance(node, ast.Raise):
                if (
                    isinstance(node.exc, ast.Call)
                    and resolve(inventory, current, node.exc) == "kotorelay.errors.Problem"
                ):
                    if (
                        len(node.exc.args) > 1
                        and ast.literal_eval(node.exc.args[1]) == "already_answered"
                    ):
                        raised(ErrorOutcome(status=409, code="already_answered", message=""))
                    else:
                        raised(problem_call(node.exc))
                elif node.exc is None:
                    if not caught:
                        raise ValueError(f"再送出元の例外が不明です: {current}:{node.lineno}")
                    exception, outcome, _, _ = caught[-1]
                    raised(outcome, exception)

                else:
                    expression(node.exc, current, stack)
                    raise ValueError(f"未対応の例外応答: {current}:{node.lineno}")
            elif isinstance(node, (ast.Break, ast.Continue)):
                add(
                    "Note over A: "
                    + (
                        "反復を終了"
                        if isinstance(node, ast.Break)
                        else "この候補の処理を終了し、次の候補へ"
                    )
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
    authenticated = uses_context or any(
        a.annotation and ast.unparse(a.annotation) == "Subject"
        for a in inventory.nodes[key].args.args
    )
    if authenticated:
        failure(
            "認証に失敗した場合",
            ErrorOutcome(status=401, code="unauthenticated", message=MESSAGES["unauthenticated"]),
        )
    if any(
        a.annotation and ast.unparse(a.annotation) not in {"Ctx", "Rt", "Subject"}
        for a in inventory.nodes[key].args.args
    ):
        failure("リクエストの入力形式が不正な場合", INVALID_INPUT, "RequestValidationError")
    if uses_context:
        add("A->>D: 依存注入でtransaction開始・組織と所属を確認")
        database_failure("DB接続")
        authentication = "kotorelay.context.Context.__init__"
        statements(inventory.nodes[authentication].body, authentication, (key, authentication))
    statements(inventory.nodes[key].body, key, (key,))
    rendered = remove_empty_blocks(lines)
    for token, (current, node) in deferred_conditions.items():
        if any(token in line for line in rendered):
            text = label(describe(inventory, current, node))
            rendered = [line.replace(token, text) for line in rendered]
    return rendered
