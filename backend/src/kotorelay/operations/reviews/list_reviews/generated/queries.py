"""DDL・SQLから生成した型付き境界。直接編集しない。
SHA256: ed55fdba04faa27e897fbd0d7982c5133f472f06d84718577e2499dd84477cdc
"""

from datetime import datetime

from pydantic import BaseModel, ConfigDict

from kotorelay.db import Database
from kotorelay.generated.models import (
    DepartmentsRow,
    DocumentsRow,
    SubmissionsRow,
    UsersRow,
    VersionsRow,
)


class DepartmentsListParams(BaseModel):
    """departments_listの束縛引数。SQLで使用する項目だけを受け付ける。"""

    model_config = ConfigDict(extra="forbid")
    organization_id: str


class DepartmentsListRow(DepartmentsRow):
    """departments_listのSELECT句に対応する取得行。"""

    model_config = ConfigDict(extra="forbid")
    id: str
    organization_id: str
    name: str
    active: bool


def departments_list(db: Database, params: DepartmentsListParams) -> list[DepartmentsListRow]:
    "現在の組織に属する部署を識別子順に一覧取得する。"
    return db.query(
        "operations/reviews/list_reviews/sql/001_departments_list.sql",
        params.model_dump(),
        DepartmentsListRow,
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
        "operations/reviews/list_reviews/sql/002_documents_list.sql",
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
        "operations/reviews/list_reviews/sql/003_submissions_list.sql",
        params.model_dump(),
        SubmissionsListRow,
    )


class UsersListParams(BaseModel):
    """users_listの束縛引数。SQLで使用する項目だけを受け付ける。"""

    model_config = ConfigDict(extra="forbid")
    organization_id: str


class UsersListRow(UsersRow):
    """users_listのSELECT句に対応する取得行。"""

    model_config = ConfigDict(extra="forbid")
    id: str
    organization_id: str
    subject: str
    display_name: str
    active: bool
    operator: bool


def users_list(db: Database, params: UsersListParams) -> list[UsersListRow]:
    "現在の組織に属する利用者を識別子順に一覧取得する。"
    return db.query(
        "operations/reviews/list_reviews/sql/004_users_list.sql", params.model_dump(), UsersListRow
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
        "operations/reviews/list_reviews/sql/005_versions_list.sql",
        params.model_dump(),
        VersionsListRow,
    )
