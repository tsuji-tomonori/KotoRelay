"""list_documentsの入力制約と応答型を定義する。"""

from __future__ import annotations

from kotorelay.generated import models

type ResponseData = list[models.DocumentsRow] | dict[str, object]
