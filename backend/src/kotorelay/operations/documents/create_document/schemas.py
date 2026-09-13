"""create_documentの入力制約と応答型を定義する。"""

from __future__ import annotations

from pydantic import Field

from kotorelay.generated import models
from kotorelay.schemas import Id, Input


class CreateDocument(Input):
    title: str = Field(min_length=1, max_length=200)
    department_id: Id


type ResponseData = models.DocumentsRow
