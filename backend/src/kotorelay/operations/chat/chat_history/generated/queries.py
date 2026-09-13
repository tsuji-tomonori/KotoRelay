"""DDL・SQLから生成した型付き境界。直接編集しない。
SHA256: 8c745274c9f260c8e64ccf7619dcf8681d3552006f9e62adccd2b1c1350aab2c
"""

from datetime import datetime

from pydantic import BaseModel, ConfigDict

from kotorelay.db import Database
from kotorelay.generated.models import (
    AnswersRow,
    ConversationsRow,
)


class AnswersListParams(BaseModel):
    """answers_listの束縛引数。SQLで使用する項目だけを受け付ける。"""

    model_config = ConfigDict(extra="forbid")
    organization_id: str


class AnswersListRow(AnswersRow):
    """answers_listのSELECT句に対応する取得行。"""

    model_config = ConfigDict(extra="forbid")
    id: str
    organization_id: str
    conversation_id: str
    user_id: str
    department_id: str
    question_key: str
    answer_key: str
    evidence: str
    status: str
    model: str
    created_at: datetime


def answers_list(db: Database, params: AnswersListParams) -> list[AnswersListRow]:
    "現在の組織に属する回答履歴を識別子順に一覧取得する。"
    return db.query(
        "operations/chat/chat_history/sql/001_answers_list.sql", params.model_dump(), AnswersListRow
    )


class ConversationsGetParams(BaseModel):
    """conversations_getの束縛引数。SQLで使用する項目だけを受け付ける。"""

    model_config = ConfigDict(extra="forbid")
    organization_id: str
    id: str


class ConversationsGetRow(ConversationsRow):
    """conversations_getのSELECT句に対応する取得行。"""

    model_config = ConfigDict(extra="forbid")
    id: str
    organization_id: str
    user_id: str
    created_at: datetime


def conversations_get(db: Database, params: ConversationsGetParams) -> list[ConversationsGetRow]:
    "現在の組織に属する指定の会話について、会話の所有者と開始日時を取得する。"
    return db.query(
        "operations/chat/chat_history/sql/002_conversations_get.sql",
        params.model_dump(),
        ConversationsGetRow,
    )
