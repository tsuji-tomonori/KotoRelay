"""chatのAPIごとのルーターを登録する。"""

from fastapi import APIRouter

from kotorelay.operations.chat.ask_question.router import router as ask_question
from kotorelay.operations.chat.chat_history.router import router as chat_history

router = APIRouter()
router.include_router(ask_question)
router.include_router(chat_history)
