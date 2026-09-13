"""correct_ocrの入力制約と応答型を定義する。"""

from __future__ import annotations

from pydantic import Field

from kotorelay.schemas import Input, Region


class OcrCorrection(Input):
    regions: list[Region] = Field(max_length=1000)
    confirmed: bool


type ResponseData = dict[str, object]
