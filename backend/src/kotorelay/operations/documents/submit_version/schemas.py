"""submit_versionの入力制約と応答型を定義する。"""

from __future__ import annotations

from pydantic import Field

from kotorelay.generated import models
from kotorelay.schemas import Input


class Submit(Input):
    revision: int = Field(ge=1)


type ResponseData = models.VersionsRow
