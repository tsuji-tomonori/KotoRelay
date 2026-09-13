"""DDL・SQLから生成した型付き境界。直接編集しない。
SHA256: 8c745274c9f260c8e64ccf7619dcf8681d3552006f9e62adccd2b1c1350aab2c
"""

from kotorelay.db import Database
from kotorelay.generated.models import (
    AnswersRow,
    ConversationsRow,
)


def answers_list(db: Database, organization_id: str) -> list[AnswersRow]:
    "現在の組織に属する回答履歴を識別子順に一覧取得する。"
    return db.query(
        "operations/chat/chat_history/sql/answers_list.sql",
        {"organization_id": organization_id},
        AnswersRow,
    )


def conversations_get(db: Database, organization_id: str, id: str) -> list[ConversationsRow]:
    "現在の組織に属する指定の会話について、会話の所有者と開始日時を取得する。"
    return db.query(
        "operations/chat/chat_history/sql/conversations_get.sql",
        {"organization_id": organization_id, "id": id},
        ConversationsRow,
    )
