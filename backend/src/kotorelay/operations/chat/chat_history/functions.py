"""chatのchat_historyの業務判定と処理を実行する。"""

from __future__ import annotations

from kotorelay.context import Context
from kotorelay.errors import require
from kotorelay.operations.chat.chat_history.generated import queries as q
from kotorelay.operations.chat.shared.functions import present
from kotorelay.schemas import AnswerView


def history(ctx: Context, conversation_id: str) -> list[AnswerView]:
    conversations = q.conversations_get(ctx.db, ctx.org, conversation_id)
    require(bool(conversations) and conversations[0].user_id == ctx.user.id)
    return [
        present(ctx, a)
        for a in sorted(q.answers_list(ctx.db, ctx.org), key=lambda a: a.created_at)
        if a.conversation_id == conversation_id
    ]
