"""DDL・SQLから生成した型付き境界。直接編集しない。
SHA256: 5da376a5721388610f01161475df58af6beae7054f52d1bc12f8aa16ead33e04
"""

from datetime import datetime

from pydantic import BaseModel, ConfigDict

from kotorelay.db import Database
from kotorelay.generated.models import (
    SubmissionsRow,
    VersionsRow,
)


class SubmissionsListParams(BaseModel):
    """submissions_listの束縛引数。SQLで使用する項目だけを受け付ける。"""

    model_config = ConfigDict(extra="forbid")
    organization_id: str


class SubmissionsListRow(SubmissionsRow):
    """submissions_listのSELECT句に対応する取得行。"""

    model_config = ConfigDict(extra="forbid")
    id: str
    organization_id: str
    document_id: str
    version_id: str
    requested_by: str
    status: str
    manifest_hash: str
    decided_by: str | None
    reason: str
    created_at: datetime
    decided_at: datetime | None


def submissions_list(db: Database, params: SubmissionsListParams) -> list[SubmissionsListRow]:
    "現在の組織に属する承認申請を識別子順に一覧取得する。"
    return db.query(
        "operations/documents/version_history/sql/001_submissions_list.sql",
        params.model_dump(),
        SubmissionsListRow,
    )


class VersionsListParams(BaseModel):
    """versions_listの束縛引数。SQLで使用する項目だけを受け付ける。"""

    model_config = ConfigDict(extra="forbid")
    organization_id: str


class VersionsListRow(VersionsRow):
    """versions_listのSELECT句に対応する取得行。"""

    model_config = ConfigDict(extra="forbid")
    id: str
    organization_id: str
    document_id: str
    number: int
    title: str
    body_key: str
    body_hash: str
    manifest: str
    manifest_hash: str
    created_by: str
    created_at: datetime


def versions_list(db: Database, params: VersionsListParams) -> list[VersionsListRow]:
    "現在の組織に属する文書版を識別子順に一覧取得する。"
    return db.query(
        "operations/documents/version_history/sql/002_versions_list.sql",
        params.model_dump(),
        VersionsListRow,
    )
