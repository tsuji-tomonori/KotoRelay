"""ask_questionの入力制約と応答型を定義する。"""

from __future__ import annotations

from pydantic import BaseModel, Field

from kotorelay.schemas import AnswerView, Citation, Id, Input


class Ask(Input):
    question: str = Field(min_length=1, max_length=2000)
    department_id: Id
    conversation_id: Id | None = None


type ResponseData = AnswerView


class Prepared(BaseModel):
    answer_id: str
    conversation_id: str
    question: str
    department_id: str
    citations: list[Citation]
    texts: list[str]
    images: list[bytes]
