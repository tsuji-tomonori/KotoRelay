"""DDL・SQLから生成した型付き境界。直接編集しない。
SHA256: 5b9972f0208b6f468bc57c3567fcf8a12a60608b644bcd14ddf6c9828185c70b
"""

from datetime import datetime

from pydantic import BaseModel, ConfigDict

from kotorelay.db import Database
from kotorelay.generated.models import (
    DepartmentsRow,
    DocumentsRow,
    IdempotencyRow,
    MembershipsRow,
    OrganizationsRow,
    UsersRow,
    VersionsRow,
)


class AuditInsertParams(BaseModel):
    """audit_insertの束縛引数。SQLで使用する項目だけを受け付ける。"""

    model_config = ConfigDict(extra="forbid")
    id: str
    organization_id: str
    user_id: str
    document_id: str | None
    version_id: str | None
    action: str
    before_state: str
    after_state: str
    reason: str
    created_at: datetime


def audit_insert(db: Database, params: AuditInsertParams) -> int:
    "現在の組織の監査記録として、操作した利用者・対象・変更前後の状態・理由を登録する。"
    return db.execute(
        "operations/system/authorization/sql/001_audit_insert.sql", params.model_dump()
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
        "operations/system/authorization/sql/002_departments_list.sql",
        params.model_dump(),
        DepartmentsListRow,
    )


class DocumentsGetParams(BaseModel):
    """documents_getの束縛引数。SQLで使用する項目だけを受け付ける。"""

    model_config = ConfigDict(extra="forbid")
    organization_id: str
    id: str


class DocumentsGetRow(DocumentsRow):
    """documents_getのSELECT句に対応する取得行。"""

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


def documents_get(db: Database, params: DocumentsGetParams) -> list[DocumentsGetRow]:
    "現在の組織に属する指定の文書について、文書の所有部署・公開範囲・状態・公開版の参照を取得する。"
    return db.query(
        "operations/system/authorization/sql/003_documents_get.sql",
        params.model_dump(),
        DocumentsGetRow,
    )


class IdempotencyGetParams(BaseModel):
    """idempotency_getの束縛引数。SQLで使用する項目だけを受け付ける。"""

    model_config = ConfigDict(extra="forbid")
    organization_id: str
    id: str


class IdempotencyGetRow(IdempotencyRow):
    """idempotency_getのSELECT句に対応する取得行。"""

    model_config = ConfigDict(extra="forbid")
    id: str
    organization_id: str
    user_id: str
    operation: str
    request_hash: str
    response: str


def idempotency_get(db: Database, params: IdempotencyGetParams) -> list[IdempotencyGetRow]:
    "現在の組織に属する指定の再送判定の記録について、実行済み操作の入力ハッシュと応答を取得する。"
    return db.query(
        "operations/system/authorization/sql/004_idempotency_get.sql",
        params.model_dump(),
        IdempotencyGetRow,
    )


class IdempotencyInsertParams(BaseModel):
    """idempotency_insertの束縛引数。SQLで使用する項目だけを受け付ける。"""

    model_config = ConfigDict(extra="forbid")
    id: str
    organization_id: str
    user_id: str
    operation: str
    request_hash: str
    response: str


def idempotency_insert(db: Database, params: IdempotencyInsertParams) -> int:
    "現在の組織の操作の再送を判定するため、実行済み操作の入力ハッシュと応答を登録する。"
    return db.execute(
        "operations/system/authorization/sql/005_idempotency_insert.sql", params.model_dump()
    )


class MembershipsListParams(BaseModel):
    """memberships_listの束縛引数。SQLで使用する項目だけを受け付ける。"""

    model_config = ConfigDict(extra="forbid")
    organization_id: str


class MembershipsListRow(MembershipsRow):
    """memberships_listのSELECT句に対応する取得行。"""

    model_config = ConfigDict(extra="forbid")
    id: str
    organization_id: str
    department_id: str
    user_id: str
    leader: bool
    can_author: bool
    can_review: bool
    active: bool


def memberships_list(db: Database, params: MembershipsListParams) -> list[MembershipsListRow]:
    "現在の組織に属する部署所属を識別子順に一覧取得する。"
    return db.query(
        "operations/system/authorization/sql/006_memberships_list.sql",
        params.model_dump(),
        MembershipsListRow,
    )


class OrganizationsFenceParams(BaseModel):
    """organizations_fenceの束縛引数。SQLで使用する項目だけを受け付ける。"""

    model_config = ConfigDict(extra="forbid")
    organization_id: str
    id: str
    revision: int


def organizations_fence(db: Database, params: OrganizationsFenceParams) -> int:
    "組織の改訂番号が一致する場合だけ番号を進め、認可判定と権限失効の競合を検出する。"
    return db.execute(
        "operations/system/authorization/sql/007_organizations_fence.sql", params.model_dump()
    )


class OrganizationsGetParams(BaseModel):
    """organizations_getの束縛引数。SQLで使用する項目だけを受け付ける。"""

    model_config = ConfigDict(extra="forbid")
    organization_id: str
    id: str


class OrganizationsGetRow(OrganizationsRow):
    """organizations_getのSELECT句に対応する取得行。"""

    model_config = ConfigDict(extra="forbid")
    id: str
    organization_id: str
    name: str
    revision: int
    suspended: bool


def organizations_get(db: Database, params: OrganizationsGetParams) -> list[OrganizationsGetRow]:
    "現在の組織の組織名・改訂番号・利用停止状態を取得する。"
    return db.query(
        "operations/system/authorization/sql/008_organizations_get.sql",
        params.model_dump(),
        OrganizationsGetRow,
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
        "operations/system/authorization/sql/009_users_list.sql", params.model_dump(), UsersListRow
    )


class VersionsGetParams(BaseModel):
    """versions_getの束縛引数。SQLで使用する項目だけを受け付ける。"""

    model_config = ConfigDict(extra="forbid")
    organization_id: str
    id: str


class VersionsGetRow(VersionsRow):
    """versions_getのSELECT句に対応する取得行。"""

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


def versions_get(db: Database, params: VersionsGetParams) -> list[VersionsGetRow]:
    "現在の組織に属する指定の文書版について、確定した本文の保存先と画像構成・検証用ハッシュを取得する。"
    return db.query(
        "operations/system/authorization/sql/010_versions_get.sql",
        params.model_dump(),
        VersionsGetRow,
    )
