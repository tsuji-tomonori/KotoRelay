"""ask_questionの入力制約と応答型を定義する。"""

from __future__ import annotations

from pydantic import Field

from kotorelay.schemas import AnswerView, Id, Input


class Ask(Input):
    question: str = Field(min_length=1, max_length=2000)
    department_id: Id
    conversation_id: Id | None = None


type ResponseData = AnswerView
