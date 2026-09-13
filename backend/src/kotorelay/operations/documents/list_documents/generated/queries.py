"""DDL・SQLから生成した型付き境界。直接編集しない。
SHA256: a874dcb8846a217994572fc3adbafbc4c22cb4e0f806451e686f56cf908479b3
"""

from datetime import datetime

from pydantic import BaseModel, ConfigDict

from kotorelay.db import Database
from kotorelay.generated.models import (
    ChunksRow,
    DocumentsRow,
    SubmissionsRow,
    VersionsRow,
)


class ChunksListParams(BaseModel):
    """chunks_listの束縛引数。SQLで使用する項目だけを受け付ける。"""

    model_config = ConfigDict(extra="forbid")
    organization_id: str


class ChunksListRow(ChunksRow):
    """chunks_listのSELECT句に対応する取得行。"""

    model_config = ConfigDict(extra="forbid")
    id: str
    organization_id: str
    document_id: str
    version_id: str
    body_key: str
    sha256: str
    heading: str
    placements: str
    manifest_hash: str
    ready: bool


def chunks_list(db: Database, params: ChunksListParams) -> list[ChunksListRow]:
    "現在の組織に属する検索用の文書断片を識別子順に一覧取得する。"
    return db.query(
        "operations/documents/list_documents/sql/001_chunks_list.sql",
        params.model_dump(),
        ChunksListRow,
    )


class DocumentsByDepartmentParams(BaseModel):
    """documents_by_departmentの束縛引数。SQLで使用する項目だけを受け付ける。"""

    model_config = ConfigDict(extra="forbid")
    organization_id: str
    department_id: str


class DocumentsByDepartmentRow(DocumentsRow):
    """documents_by_departmentのSELECT句に対応する取得行。"""

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


def documents_by_department(
    db: Database, params: DocumentsByDepartmentParams
) -> list[DocumentsByDepartmentRow]:
    "現在の組織に属する文書を指定した所有部署で絞り込み、一覧の対象を取得する。"
    return db.query(
        "operations/documents/list_documents/sql/002_documents_by_department.sql",
        params.model_dump(),
        DocumentsByDepartmentRow,
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
        "operations/documents/list_documents/sql/003_documents_list.sql",
        params.model_dump(),
        DocumentsListRow,
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
        "operations/documents/list_documents/sql/004_submissions_list.sql",
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
        "operations/documents/list_documents/sql/005_versions_list.sql",
        params.model_dump(),
        VersionsListRow,
    )
