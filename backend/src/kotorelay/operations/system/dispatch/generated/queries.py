"""DDL・SQLから生成した型付き境界。直接編集しない。
SHA256: cce97c744d57b159d52bf57473ef3cb8be296952f1742a2c4fc9f8c6f33e6d6c
"""

from datetime import datetime

from pydantic import BaseModel, ConfigDict

from kotorelay.db import Database
from kotorelay.generated.models import (
    OutboxRow,
)


class OutboxListParams(BaseModel):
    """outbox_listの束縛引数。SQLで使用する項目だけを受け付ける。"""

    model_config = ConfigDict(extra="forbid")
    organization_id: str


class OutboxListRow(OutboxRow):
    """outbox_listのSELECT句に対応する取得行。"""

    model_config = ConfigDict(extra="forbid")
    id: str
    organization_id: str
    document_id: str
    version_id: str | None
    kind: str
    status: str
    attempts: int
    error_code: str
    created_at: datetime


def outbox_list(db: Database, params: OutboxListParams) -> list[OutboxListRow]:
    "現在の組織に属する反映・削除ジョブを識別子順に一覧取得する。"
    return db.query(
        "operations/system/dispatch/sql/001_outbox_list.sql", params.model_dump(), OutboxListRow
    )
