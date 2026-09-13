"""ask_questionのHTTP入力と業務処理の順序を宣言する。"""

from fastapi import APIRouter

from kotorelay.http_types import Key
from kotorelay.operations.chat.ask_question import functions as f
from kotorelay.operations.chat.ask_question.contract import CONTRACT
from kotorelay.operations.chat.ask_question.response_builders import build_response
from kotorelay.operations.chat.ask_question.samples import SAMPLES
from kotorelay.operations.chat.ask_question.schemas import Ask
from kotorelay.runtime import Rt, Subject
from kotorelay.schemas import AnswerView

router = APIRouter(prefix="/api/chat", tags=["RAGチャット"])


@router.post(
    "",
    summary="最新承認版の根拠で回答",
    operation_id="ask_question",
    openapi_extra=CONTRACT.openapi_extra(SAMPLES),
)
def ask_question(rt: Rt, subject: Subject, data: Ask, key: Key) -> AnswerView:
    return build_response(f.ask(rt, subject, data, str(key)))
