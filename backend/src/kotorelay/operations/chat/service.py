"""外部モデル呼び出しをDB transactionの外で実行する。"""

from botocore.exceptions import BotoCoreError, ClientError

from kotorelay.errors import Problem
from kotorelay.generated import queries as q
from kotorelay.operations.chat import functions as f
from kotorelay.runtime import Runtime
from kotorelay.schemas import AnswerView, Ask


def ask(rt: Runtime, subject: str, data: Ask, key: str) -> AnswerView:
    try:
        with rt.context(subject) as ctx:
            prepared = f.prepare(ctx, data, key, rt.engine)
    except Problem as exc:
        if exc.code != "already_answered":
            raise
        with rt.context(subject) as ctx:
            return f.present(ctx, q.answers_get(ctx.db, ctx.org, exc.message)[0])
    failed = False
    answer = ""
    if prepared.citations:
        # 検索とモデル入力の間に確定した失効を改めて検出する。
        with rt.context(subject) as ctx:
            if not all(f.validate_citation(ctx, c) for c in prepared.citations):
                prepared = prepared.model_copy(update={"citations": [], "texts": [], "images": []})
        if prepared.citations:
            try:
                answer = rt.engine.generate(prepared.question, prepared.texts, prepared.images)
            except (BotoCoreError, ClientError, TimeoutError):
                failed = True
    with rt.context(subject) as ctx:
        return f.finalize(ctx, prepared, answer, rt.engine, failed)
