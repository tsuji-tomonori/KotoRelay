"""DDL・SQLから生成した型付き境界。直接編集しない。
SHA256: 4677d1201bf137cf7b6ffd7f3e38a53a11af6b303681a7110df446f144650f8e
"""

from pydantic import BaseModel, ConfigDict

from kotorelay.db import Database
from kotorelay.generated.models import (
    DraftsRow,
)


class DraftsListParams(BaseModel):
    """drafts_listの束縛引数。SQLで使用する項目だけを受け付ける。"""

    model_config = ConfigDict(extra="forbid")
    organization_id: str


class DraftsListRow(DraftsRow):
    """drafts_listのSELECT句に対応する取得行。"""

    model_config = ConfigDict(extra="forbid")
    id: str
    organization_id: str
    document_id: str
    body_key: str
    body_hash: str
    placements: str
    revision: int
    updated_by: str


def drafts_list(db: Database, params: DraftsListParams) -> list[DraftsListRow]:
    "現在の組織に属する下書きを識別子順に一覧取得する。"
    return db.query(
        "operations/documents/shared/sql/001_drafts_list.sql", params.model_dump(), DraftsListRow
    )
