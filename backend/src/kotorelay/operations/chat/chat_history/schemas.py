"""chat_historyの入力制約と応答型を定義する。"""

from __future__ import annotations

from kotorelay.schemas import AnswerView

type ResponseData = list[AnswerView]
