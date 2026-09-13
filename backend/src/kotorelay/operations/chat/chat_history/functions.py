"""chatのchat_historyの業務判定と処理を実行する。"""

from __future__ import annotations

import uuid

import kotorelay.context as context_types
import kotorelay.operations.chat.chat_history.generated.queries as q
import kotorelay.schemas as shared_schemas
from kotorelay.errors import require
from kotorelay.operations.chat.shared.functions import present


def conversations_get(
    ctx: context_types.Context, conversation_id: uuid.UUID
) -> list[q.ConversationsGetRow]:
    """現在の組織に属する指定の会話について、会話の所有者と開始日時を取得する。"""
    return q.conversations_get(
        ctx.db, q.ConversationsGetParams(organization_id=ctx.org, id=str(conversation_id))
    )


def require_conversation_owner(
    conversations: list[q.ConversationsGetRow], ctx: context_types.Context
) -> None:
    """取得対象の会話を現在の利用者が所有していることを確認する。"""
    return require(bool(conversations) and conversations[0].user_id == ctx.user.id)


def select_chat_history(
    ctx: context_types.Context, conversation_id: uuid.UUID
) -> list[shared_schemas.AnswerView]:
    """用途と対象に一致するデータだけを取り出す。"""
    return [
        present(ctx, a)
        for a in sorted(
            q.answers_list(ctx.db, q.AnswersListParams(organization_id=ctx.org)),
            key=lambda a: a.created_at,
        )
        if a.conversation_id == str(conversation_id)
    ]
