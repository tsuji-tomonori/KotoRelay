"""実在する例外送出と型付き運用ログから応答・メッセージ設計を生成する。"""

from __future__ import annotations

import ast
from inspect import formatannotation

from kotorelay.error_responses import DB_CONFLICT, INVALID_INPUT, UNAVAILABLE, ErrorOutcome
from kotorelay.errors import MESSAGES
from kotorelay.operational_logging import CATALOG, MessageId, OperationalLogContext


def problem_call(node: ast.Call, *, require: bool = False) -> ErrorOutcome:
    """requireの省略引数とキーワード引数も実装と同じ既定値へ解決する。"""
    names = ["condition", "code", "status"] if require else ["status", "code", "message"]
    values = {name: value for name, value in zip(names, node.args, strict=False)}
    values.update({k.arg: k.value for k in node.keywords if k.arg})
    try:
        code = ast.literal_eval(values.get("code", ast.Constant("not_found")))
        status = ast.literal_eval(values.get("status", ast.Constant(404)))
        message = (
            MESSAGES.get(code, "対象を利用できません。")
            if require
            else ast.literal_eval(values["message"])
        )
    except (ValueError, KeyError) as exc:
        raise ValueError(f"例外応答を静的に解決できません: {ast.unparse(node)}") from exc
    return ErrorOutcome(status=status, code=code, message=message)


def response_label(outcome: ErrorOutcome) -> str:
    return (
        f'HTTP {outcome.status} / {{code: "{outcome.code}", '
        f'message: "{outcome.message}", request_id: 相関ID}}'
    )


def contracts(inventory, reached: list[str], *, authenticated: bool) -> list[ErrorOutcome]:
    """到達する実装に定義された応答を列挙する。内部で捕捉するProblemは送出表に注記する。"""
    outcomes = [INVALID_INPUT, DB_CONFLICT, UNAVAILABLE] if authenticated else []
    if authenticated:
        outcomes.append(
            ErrorOutcome(status=401, code="unauthenticated", message=MESSAGES["unauthenticated"])
        )
    for key in reached:
        if key == "kotorelay.errors.require":
            continue
        for node in ast.walk(inventory.nodes[key]):
            if not isinstance(node, ast.Call):
                continue
            from tools.project.router_sequence import resolve

            target = resolve(inventory, key, node)
            if target == "kotorelay.errors.require":
                outcomes.append(problem_call(node, require=True))
            elif target == "kotorelay.errors.Problem":
                if len(node.args) > 1 and ast.literal_eval(node.args[1]) == "already_answered":
                    continue
                outcomes.append(problem_call(node))
    unique = {(r.status, r.code, r.message): r for r in outcomes}
    return [unique[k] for k in sorted(unique)]


def message_sections(
    inventory, reached: list[str], outcomes: list[ErrorOutcome], operation: str, endpoint: str
) -> list[str]:
    from tools.project.design import ROOT, table

    locations: dict[MessageId, list[str]] = {}
    if outcomes:
        for event in [MessageId.HTTP_REJECTED, MessageId.HTTP_FAILED]:
            locations[event] = ["backend/src/kotorelay/main.py:error_response"]
    for key in reached:
        for node in ast.walk(inventory.nodes[key]):
            if isinstance(node, ast.Call) and ast.unparse(node.func) in {
                "ops_logger.error",
                "ops_logger.warning",
            }:
                event = MessageId[ast.unparse(node.args[0]).split(".")[-1]]
                if ast.unparse(node.func).split(".")[-1].upper() != CATALOG[event].level:
                    raise ValueError(f"ログcatalogと呼出しlevelの不一致: {key}")
                locations.setdefault(event, []).append(
                    f"{inventory.paths[key].relative_to(ROOT)}:{node.lineno}"
                )
    details = []
    for event, paths in sorted(locations.items()):
        definition = CATALOG[event]
        details.append(
            f"### `{event.value}`\n\n"
            + table(
                ["項目", "内容"],
                [
                    ["level", definition.level],
                    ["メッセージ", definition.summary],
                    ["例外・出力条件", definition.when],
                    ["返すレスポンス", definition.response],
                    ["呼出し位置", ", ".join(paths)],
                    ["確認手順", definition.check_procedure],
                    ["復旧手順", definition.remediation_procedure],
                ],
            )
        )
    details.append(
        "### 例外からHTTPエラー応答への対応\n\n"
        "以下は例外が内部で処理されずHTTP境界に到達した場合の応答です。"
        "内部で捕捉して継続する経路はシーケンスのcatchと上記ログ別の継続結果を参照してください。\n\n"
        + table(
            ["例外", "HTTP", "code", "message", "ログID"],
            [
                [
                    "RequestValidationError"
                    if r.code == "invalid_input"
                    else "psycopg.Error"
                    if r == DB_CONFLICT
                    else "psycopg.Error / BotoCoreError / ClientError / OSError / TimeoutError"
                    if r == UNAVAILABLE
                    else "Problem",
                    r.status,
                    r.code,
                    r.message,
                    MessageId.HTTP_FAILED.value
                    if r.status >= 500
                    else MessageId.HTTP_REJECTED.value,
                ]
                for r in outcomes
            ],
        )
    )
    details.append(
        "### 型付き出力項目\n\n"
        + table(
            ["項目", "型", "内容"],
            [
                [name, formatannotation(field.annotation), field.description]
                for name, field in OperationalLogContext.model_fields.items()
            ],
        )
    )
    return [
        table(["項目", "値"], [["operation", operation], ["endpoint", endpoint]]),
        "lazunexのops_loggerと同じく、独自型のcontext、ログID、例外型、応答、確認・復旧手順を必須にします。"
        "実行時catalogと実際のops_logger呼出しから生成します。"
        "通常アクセスのINFO KR_REQUESTは相関ID・メソッド・statusだけを記録します。",
        table(
            ["message_id", "level", "ログ概要"],
            [
                [event.value, CATALOG[event].level, CATALOG[event].summary]
                for event in sorted(locations)
            ],
        ),
        "\n\n".join(details),
        "型・catalogの未登録ID、未知context項目、level不一致を拒否します。"
        "例外の生メッセージ、本文、JWT、OCR原文は渡しません。HTTPエラーにはrequest_idを付け、同じIDのログと照合します。",
    ]


def validate_logging(app):
    """運用ログの迂回とcatalog未登録呼出しを全backend sourceで検出する。"""
    for path in app.rglob("*.py"):
        tree = ast.parse(path.read_text())
        for node in ast.walk(tree):
            if isinstance(node, (ast.Import, ast.ImportFrom)):
                imported = (
                    [a.name for a in node.names]
                    if isinstance(node, ast.Import)
                    else [node.module or ""]
                )
                if "logging" in imported and path.name not in {"main.py", "operational_logging.py"}:
                    raise ValueError(f"運用ログは型付きops_loggerを使用する: {path}:{node.lineno}")
            if not isinstance(node, ast.Call) or not isinstance(node.func, ast.Attribute):
                continue
            if node.func.attr not in {"warning", "error", "exception", "critical"}:
                continue
            name = ast.unparse(node.func)
            if name not in {"ops_logger.warning", "ops_logger.error"}:
                raise ValueError(f"型付きログ以外の呼出し: {path}:{node.lineno}")
            if (
                not node.args
                or not isinstance(node.args[0], ast.Attribute)
                or ast.unparse(node.args[0].value) != "MessageId"
            ):
                raise ValueError(f"ログIDは登録済みMessageIdが必要: {path}:{node.lineno}")
            try:
                event = MessageId[node.args[0].attr]
            except KeyError as exc:
                raise ValueError(f"未登録ログID: {path}:{node.lineno}") from exc
            if CATALOG[event].level != node.func.attr.upper() or {k.arg for k in node.keywords} != {
                "context_model"
            }:
                raise ValueError(f"ログlevelまたは型付きcontextが不正: {path}:{node.lineno}")
