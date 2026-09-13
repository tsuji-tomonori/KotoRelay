"""chat_historyのHTTP入力と業務処理の順序を宣言する。"""

from uuid import UUID

from fastapi import APIRouter

from kotorelay.operations.chat.chat_history import functions as f
from kotorelay.operations.chat.chat_history.contract import CONTRACT
from kotorelay.operations.chat.chat_history.response_builders import build_response
from kotorelay.operations.chat.chat_history.samples import SAMPLES
from kotorelay.runtime import Ctx
from kotorelay.schemas import AnswerView

router = APIRouter(prefix="/api/chat", tags=["RAGチャット"])


@router.get(
    "/{conversation_id}",
    summary="現行認可で会話履歴を再表示",
    operation_id="chat_history",
    openapi_extra=CONTRACT.openapi_extra(SAMPLES),
)
def chat_history(ctx: Ctx, conversation_id: UUID) -> list[AnswerView]:
    return build_response(f.history(ctx, str(conversation_id)))
