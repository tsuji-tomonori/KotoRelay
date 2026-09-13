"""decide_reviewの入力制約と応答型を定義する。"""

from __future__ import annotations

from typing import Literal

from pydantic import Field

from kotorelay.generated import models
from kotorelay.schemas import Input


class Decide(Input):
    manifest_hash: str = Field(pattern="^[0-9a-f]{64}$")
    decision: Literal["approved", "rejected"]
    reason: str = Field(default="", max_length=2000)


type ResponseData = models.SubmissionsRow
