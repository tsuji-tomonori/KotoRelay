"""change_policyの入力制約と応答型を定義する。"""

from __future__ import annotations

from typing import Literal

from pydantic import Field

from kotorelay.generated import models
from kotorelay.schemas import Id, Input


class ChangePolicy(Input):
    reason: str = Field(default="", max_length=2000)
    revision: int = Field(ge=1)
    visibility: Literal["department", "selected", "organization"]
    shared_departments: list[Id] = Field(default_factory=list, max_length=30)
    status: Literal["active", "withdrawn", "deleted"]


type ResponseData = models.DocumentsRow
