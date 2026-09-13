"""DDL・SQLから生成した型付き境界。直接編集しない。
SHA256: 8cdc42f5241337721cba6453c80f16a537254b677e7844973ad72096a381956d
"""

from datetime import datetime

from pydantic import BaseModel, ConfigDict

from kotorelay.db import Database
from kotorelay.generated.models import (
    DocumentsRow,
    OutboxRow,
    VersionsRow,
)


class DocumentsListParams(BaseModel):
    """documents_listの束縛引数。SQLで使用する項目だけを受け付ける。"""

    model_config = ConfigDict(extra="forbid")
    organization_id: str


class DocumentsListRow(DocumentsRow):
    """documents_listのSELECT句に対応する取得行。"""

    model_config = ConfigDict(extra="forbid")
    id: str
    organization_id: str
    department_id: str
    title: str
    created_by: str
    visibility: str
    shared_departments: str
    status: str
    revision: int
    next_version: int
    latest_version_id: str | None
    updated_at: datetime


def documents_list(db: Database, params: DocumentsListParams) -> list[DocumentsListRow]:
    "現在の組織に属する文書を識別子順に一覧取得する。"
    return db.query(
        "operations/indexing/list_jobs/sql/001_documents_list.sql",
        params.model_dump(),
        DocumentsListRow,
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
        "operations/indexing/list_jobs/sql/002_outbox_list.sql", params.model_dump(), OutboxListRow
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
        "operations/indexing/list_jobs/sql/003_versions_list.sql",
        params.model_dump(),
        VersionsListRow,
    )
