"""根拠を再取得するチャットAPIを公開する。"""

from uuid import UUID

from fastapi import APIRouter

from kotorelay.operations.chat import functions as f
from kotorelay.operations.chat import service
from kotorelay.operations.documents.router import Key
from kotorelay.runtime import Ctx, Rt, Subject
from kotorelay.schemas import AnswerView, Ask

router = APIRouter(prefix="/api/chat", tags=["RAGチャット"])


@router.post("", summary="最新承認版の根拠で回答", operation_id="ask_question")
def ask_question(rt: Rt, subject: Subject, data: Ask, key: Key) -> AnswerView:
    return service.ask(rt, subject, data, str(key))


@router.get("/{conversation_id}", summary="現行認可で会話履歴を再表示", operation_id="chat_history")
def chat_history(ctx: Ctx, conversation_id: UUID) -> list[AnswerView]:
    return f.history(ctx, str(conversation_id))
