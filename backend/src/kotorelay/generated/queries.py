"""DDL・SQLから生成した型付き境界。直接編集しない。
SHA256: 777b86c16c6d2948719aa1b092c5a7d7018c30a6757511e4c73bcb4bc04a6191
"""

from datetime import datetime

from pydantic import BaseModel

from kotorelay.db import Database


class OrganizationsRow(BaseModel):
    """organizationsのDDL由来の行型。"""

    id: str
    organization_id: str
    name: str
    revision: int
    suspended: bool


class UsersRow(BaseModel):
    """usersのDDL由来の行型。"""

    id: str
    organization_id: str
    subject: str
    display_name: str
    active: bool
    operator: bool


class DepartmentsRow(BaseModel):
    """departmentsのDDL由来の行型。"""

    id: str
    organization_id: str
    name: str
    active: bool


class MembershipsRow(BaseModel):
    """membershipsのDDL由来の行型。"""

    id: str
    organization_id: str
    department_id: str
    user_id: str
    leader: bool
    can_author: bool
    can_review: bool
    active: bool


class DocumentsRow(BaseModel):
    """documentsのDDL由来の行型。"""

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


class DraftsRow(BaseModel):
    """draftsのDDL由来の行型。"""

    id: str
    organization_id: str
    document_id: str
    body_key: str
    body_hash: str
    placements: str
    revision: int
    updated_by: str


class VersionsRow(BaseModel):
    """versionsのDDL由来の行型。"""

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


class SubmissionsRow(BaseModel):
    """submissionsのDDL由来の行型。"""

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


class AssetsRow(BaseModel):
    """assetsのDDL由来の行型。"""

    id: str
    organization_id: str
    document_id: str
    object_key: str
    sha256: str
    media_type: str
    width: int
    height: int
    size: int
    created_at: datetime


class OcrRunsRow(BaseModel):
    """ocr_runsのDDL由来の行型。"""

    id: str
    organization_id: str
    document_id: str
    asset_id: str
    result_key: str
    result_hash: str
    engine: str
    status: str
    confirmed: bool
    created_at: datetime


class ChunksRow(BaseModel):
    """chunksのDDL由来の行型。"""

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


class OutboxRow(BaseModel):
    """outboxのDDL由来の行型。"""

    id: str
    organization_id: str
    document_id: str
    version_id: str | None
    kind: str
    status: str
    attempts: int
    error_code: str
    created_at: datetime


class ConversationsRow(BaseModel):
    """conversationsのDDL由来の行型。"""

    id: str
    organization_id: str
    user_id: str
    created_at: datetime


class AnswersRow(BaseModel):
    """answersのDDL由来の行型。"""

    id: str
    organization_id: str
    conversation_id: str
    user_id: str
    department_id: str
    question_key: str
    answer_key: str
    evidence: str
    status: str
    model: str
    created_at: datetime


class EventsRow(BaseModel):
    """eventsのDDL由来の行型。"""

    id: str
    organization_id: str
    user_id: str
    department_id: str
    document_id: str | None
    answer_id: str | None
    kind: str
    outcome: str
    created_at: datetime


class IdempotencyRow(BaseModel):
    """idempotencyのDDL由来の行型。"""

    id: str
    organization_id: str
    user_id: str
    operation: str
    request_hash: str
    response: str


class AuditRow(BaseModel):
    """auditのDDL由来の行型。"""

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


def answers_delete(db: Database, organization_id: str, id: str) -> int:
    """answersの指定行だけを削除する。"""
    return db.execute(
        "operations/chat/sql/answers_delete.sql", {"organization_id": organization_id, "id": id}
    )


def answers_get(db: Database, organization_id: str, id: str) -> list[AnswersRow]:
    """answersを認証組織の範囲で取得する。"""
    return db.query(
        "operations/chat/sql/answers_get.sql",
        {"organization_id": organization_id, "id": id},
        AnswersRow,
    )


def answers_insert(db: Database, row: AnswersRow) -> int:
    """answersの型検査済み行を保存する。"""
    return db.execute("operations/chat/sql/answers_insert.sql", row.model_dump())


def answers_list(db: Database, organization_id: str) -> list[AnswersRow]:
    """answersを認証組織の範囲で取得する。"""
    return db.query(
        "operations/chat/sql/answers_list.sql", {"organization_id": organization_id}, AnswersRow
    )


def answers_update(db: Database, row: AnswersRow) -> int:
    """answersの型検査済み行を保存する。"""
    return db.execute("operations/chat/sql/answers_update.sql", row.model_dump())


def conversations_delete(db: Database, organization_id: str, id: str) -> int:
    """conversationsの指定行だけを削除する。"""
    return db.execute(
        "operations/chat/sql/conversations_delete.sql",
        {"organization_id": organization_id, "id": id},
    )


def conversations_get(db: Database, organization_id: str, id: str) -> list[ConversationsRow]:
    """conversationsを認証組織の範囲で取得する。"""
    return db.query(
        "operations/chat/sql/conversations_get.sql",
        {"organization_id": organization_id, "id": id},
        ConversationsRow,
    )


def conversations_insert(db: Database, row: ConversationsRow) -> int:
    """conversationsの型検査済み行を保存する。"""
    return db.execute("operations/chat/sql/conversations_insert.sql", row.model_dump())


def conversations_list(db: Database, organization_id: str) -> list[ConversationsRow]:
    """conversationsを認証組織の範囲で取得する。"""
    return db.query(
        "operations/chat/sql/conversations_list.sql",
        {"organization_id": organization_id},
        ConversationsRow,
    )


def conversations_update(db: Database, row: ConversationsRow) -> int:
    """conversationsの型検査済み行を保存する。"""
    return db.execute("operations/chat/sql/conversations_update.sql", row.model_dump())


def documents_by_department(
    db: Database, organization_id: str, department_id: str
) -> list[DocumentsRow]:
    """documentsを認証組織の範囲で取得する。"""
    return db.query(
        "operations/documents/sql/documents_by_department.sql",
        {"organization_id": organization_id, "department_id": department_id},
        DocumentsRow,
    )


def documents_delete(db: Database, organization_id: str, id: str) -> int:
    """documentsの指定行だけを削除する。"""
    return db.execute(
        "operations/documents/sql/documents_delete.sql",
        {"organization_id": organization_id, "id": id},
    )


def documents_get(db: Database, organization_id: str, id: str) -> list[DocumentsRow]:
    """documentsを認証組織の範囲で取得する。"""
    return db.query(
        "operations/documents/sql/documents_get.sql",
        {"organization_id": organization_id, "id": id},
        DocumentsRow,
    )


def documents_insert(db: Database, row: DocumentsRow) -> int:
    """documentsの型検査済み行を保存する。"""
    return db.execute("operations/documents/sql/documents_insert.sql", row.model_dump())


def documents_list(db: Database, organization_id: str) -> list[DocumentsRow]:
    """documentsを認証組織の範囲で取得する。"""
    return db.query(
        "operations/documents/sql/documents_list.sql",
        {"organization_id": organization_id},
        DocumentsRow,
    )


def documents_update(db: Database, row: DocumentsRow) -> int:
    """documentsの型検査済み行を保存する。"""
    return db.execute("operations/documents/sql/documents_update.sql", row.model_dump())


def drafts_delete(db: Database, organization_id: str, id: str) -> int:
    """draftsの指定行だけを削除する。"""
    return db.execute(
        "operations/documents/sql/drafts_delete.sql", {"organization_id": organization_id, "id": id}
    )


def drafts_get(db: Database, organization_id: str, id: str) -> list[DraftsRow]:
    """draftsを認証組織の範囲で取得する。"""
    return db.query(
        "operations/documents/sql/drafts_get.sql",
        {"organization_id": organization_id, "id": id},
        DraftsRow,
    )


def drafts_insert(db: Database, row: DraftsRow) -> int:
    """draftsの型検査済み行を保存する。"""
    return db.execute("operations/documents/sql/drafts_insert.sql", row.model_dump())


def drafts_list(db: Database, organization_id: str) -> list[DraftsRow]:
    """draftsを認証組織の範囲で取得する。"""
    return db.query(
        "operations/documents/sql/drafts_list.sql", {"organization_id": organization_id}, DraftsRow
    )


def drafts_update(db: Database, row: DraftsRow) -> int:
    """draftsの型検査済み行を保存する。"""
    return db.execute("operations/documents/sql/drafts_update.sql", row.model_dump())


def versions_delete(db: Database, organization_id: str, id: str) -> int:
    """versionsの指定行だけを削除する。"""
    return db.execute(
        "operations/documents/sql/versions_delete.sql",
        {"organization_id": organization_id, "id": id},
    )


def versions_get(db: Database, organization_id: str, id: str) -> list[VersionsRow]:
    """versionsを認証組織の範囲で取得する。"""
    return db.query(
        "operations/documents/sql/versions_get.sql",
        {"organization_id": organization_id, "id": id},
        VersionsRow,
    )


def versions_insert(db: Database, row: VersionsRow) -> int:
    """versionsの型検査済み行を保存する。"""
    return db.execute("operations/documents/sql/versions_insert.sql", row.model_dump())


def versions_list(db: Database, organization_id: str) -> list[VersionsRow]:
    """versionsを認証組織の範囲で取得する。"""
    return db.query(
        "operations/documents/sql/versions_list.sql",
        {"organization_id": organization_id},
        VersionsRow,
    )


def departments_get(db: Database, organization_id: str, id: str) -> list[DepartmentsRow]:
    """departmentsを認証組織の範囲で取得する。"""
    return db.query(
        "operations/groups/sql/departments_get.sql",
        {"organization_id": organization_id, "id": id},
        DepartmentsRow,
    )


def departments_insert(db: Database, row: DepartmentsRow) -> int:
    """departmentsの型検査済み行を保存する。"""
    return db.execute("operations/groups/sql/departments_insert.sql", row.model_dump())


def departments_list(db: Database, organization_id: str) -> list[DepartmentsRow]:
    """departmentsを認証組織の範囲で取得する。"""
    return db.query(
        "operations/groups/sql/departments_list.sql",
        {"organization_id": organization_id},
        DepartmentsRow,
    )


def departments_update(db: Database, row: DepartmentsRow) -> int:
    """departmentsの型検査済み行を保存する。"""
    return db.execute("operations/groups/sql/departments_update.sql", row.model_dump())


def memberships_delete(db: Database, organization_id: str, id: str) -> int:
    """membershipsの指定行だけを削除する。"""
    return db.execute(
        "operations/groups/sql/memberships_delete.sql",
        {"organization_id": organization_id, "id": id},
    )


def memberships_get(db: Database, organization_id: str, id: str) -> list[MembershipsRow]:
    """membershipsを認証組織の範囲で取得する。"""
    return db.query(
        "operations/groups/sql/memberships_get.sql",
        {"organization_id": organization_id, "id": id},
        MembershipsRow,
    )


def memberships_insert(db: Database, row: MembershipsRow) -> int:
    """membershipsの型検査済み行を保存する。"""
    return db.execute("operations/groups/sql/memberships_insert.sql", row.model_dump())


def memberships_list(db: Database, organization_id: str) -> list[MembershipsRow]:
    """membershipsを認証組織の範囲で取得する。"""
    return db.query(
        "operations/groups/sql/memberships_list.sql",
        {"organization_id": organization_id},
        MembershipsRow,
    )


def memberships_update(db: Database, row: MembershipsRow) -> int:
    """membershipsの型検査済み行を保存する。"""
    return db.execute("operations/groups/sql/memberships_update.sql", row.model_dump())


def organizations_fence(db: Database, row: OrganizationsRow) -> int:
    """organizationsの型検査済み行を保存する。"""
    return db.execute("operations/identity/sql/organizations_fence.sql", row.model_dump())


def organizations_get(db: Database, organization_id: str, id: str) -> list[OrganizationsRow]:
    """organizationsを認証組織の範囲で取得する。"""
    return db.query(
        "operations/identity/sql/organizations_get.sql",
        {"organization_id": organization_id, "id": id},
        OrganizationsRow,
    )


def organizations_insert(db: Database, row: OrganizationsRow) -> int:
    """organizationsの型検査済み行を保存する。"""
    return db.execute("operations/identity/sql/organizations_insert.sql", row.model_dump())


def organizations_list(db: Database, organization_id: str) -> list[OrganizationsRow]:
    """organizationsを認証組織の範囲で取得する。"""
    return db.query(
        "operations/identity/sql/organizations_list.sql",
        {"organization_id": organization_id},
        OrganizationsRow,
    )


def organizations_update(db: Database, row: OrganizationsRow) -> int:
    """organizationsの型検査済み行を保存する。"""
    return db.execute("operations/identity/sql/organizations_update.sql", row.model_dump())


def users_get(db: Database, organization_id: str, id: str) -> list[UsersRow]:
    """usersを認証組織の範囲で取得する。"""
    return db.query(
        "operations/identity/sql/users_get.sql",
        {"organization_id": organization_id, "id": id},
        UsersRow,
    )


def users_insert(db: Database, row: UsersRow) -> int:
    """usersの型検査済み行を保存する。"""
    return db.execute("operations/identity/sql/users_insert.sql", row.model_dump())


def users_list(db: Database, organization_id: str) -> list[UsersRow]:
    """usersを認証組織の範囲で取得する。"""
    return db.query(
        "operations/identity/sql/users_list.sql", {"organization_id": organization_id}, UsersRow
    )


def users_update(db: Database, row: UsersRow) -> int:
    """usersの型検査済み行を保存する。"""
    return db.execute("operations/identity/sql/users_update.sql", row.model_dump())


def assets_delete(db: Database, organization_id: str, id: str) -> int:
    """assetsの指定行だけを削除する。"""
    return db.execute(
        "operations/images/sql/assets_delete.sql", {"organization_id": organization_id, "id": id}
    )


def assets_get(db: Database, organization_id: str, id: str) -> list[AssetsRow]:
    """assetsを認証組織の範囲で取得する。"""
    return db.query(
        "operations/images/sql/assets_get.sql",
        {"organization_id": organization_id, "id": id},
        AssetsRow,
    )


def assets_insert(db: Database, row: AssetsRow) -> int:
    """assetsの型検査済み行を保存する。"""
    return db.execute("operations/images/sql/assets_insert.sql", row.model_dump())


def assets_list(db: Database, organization_id: str) -> list[AssetsRow]:
    """assetsを認証組織の範囲で取得する。"""
    return db.query(
        "operations/images/sql/assets_list.sql", {"organization_id": organization_id}, AssetsRow
    )


def ocr_runs_delete(db: Database, organization_id: str, id: str) -> int:
    """ocr_runsの指定行だけを削除する。"""
    return db.execute(
        "operations/images/sql/ocr_runs_delete.sql", {"organization_id": organization_id, "id": id}
    )


def ocr_runs_get(db: Database, organization_id: str, id: str) -> list[OcrRunsRow]:
    """ocr_runsを認証組織の範囲で取得する。"""
    return db.query(
        "operations/images/sql/ocr_runs_get.sql",
        {"organization_id": organization_id, "id": id},
        OcrRunsRow,
    )


def ocr_runs_insert(db: Database, row: OcrRunsRow) -> int:
    """ocr_runsの型検査済み行を保存する。"""
    return db.execute("operations/images/sql/ocr_runs_insert.sql", row.model_dump())


def ocr_runs_list(db: Database, organization_id: str) -> list[OcrRunsRow]:
    """ocr_runsを認証組織の範囲で取得する。"""
    return db.query(
        "operations/images/sql/ocr_runs_list.sql", {"organization_id": organization_id}, OcrRunsRow
    )


def chunks_delete(db: Database, organization_id: str, id: str) -> int:
    """chunksの指定行だけを削除する。"""
    return db.execute(
        "operations/indexing/sql/chunks_delete.sql", {"organization_id": organization_id, "id": id}
    )


def chunks_get(db: Database, organization_id: str, id: str) -> list[ChunksRow]:
    """chunksを認証組織の範囲で取得する。"""
    return db.query(
        "operations/indexing/sql/chunks_get.sql",
        {"organization_id": organization_id, "id": id},
        ChunksRow,
    )


def chunks_insert(db: Database, row: ChunksRow) -> int:
    """chunksの型検査済み行を保存する。"""
    return db.execute("operations/indexing/sql/chunks_insert.sql", row.model_dump())


def chunks_list(db: Database, organization_id: str) -> list[ChunksRow]:
    """chunksを認証組織の範囲で取得する。"""
    return db.query(
        "operations/indexing/sql/chunks_list.sql", {"organization_id": organization_id}, ChunksRow
    )


def chunks_update(db: Database, row: ChunksRow) -> int:
    """chunksの型検査済み行を保存する。"""
    return db.execute("operations/indexing/sql/chunks_update.sql", row.model_dump())


def outbox_delete(db: Database, organization_id: str, id: str) -> int:
    """outboxの指定行だけを削除する。"""
    return db.execute(
        "operations/indexing/sql/outbox_delete.sql", {"organization_id": organization_id, "id": id}
    )


def outbox_get(db: Database, organization_id: str, id: str) -> list[OutboxRow]:
    """outboxを認証組織の範囲で取得する。"""
    return db.query(
        "operations/indexing/sql/outbox_get.sql",
        {"organization_id": organization_id, "id": id},
        OutboxRow,
    )


def outbox_insert(db: Database, row: OutboxRow) -> int:
    """outboxの型検査済み行を保存する。"""
    return db.execute("operations/indexing/sql/outbox_insert.sql", row.model_dump())


def outbox_list(db: Database, organization_id: str) -> list[OutboxRow]:
    """outboxを認証組織の範囲で取得する。"""
    return db.query(
        "operations/indexing/sql/outbox_list.sql", {"organization_id": organization_id}, OutboxRow
    )


def outbox_update(db: Database, row: OutboxRow) -> int:
    """outboxの型検査済み行を保存する。"""
    return db.execute("operations/indexing/sql/outbox_update.sql", row.model_dump())


def events_get(db: Database, organization_id: str, id: str) -> list[EventsRow]:
    """eventsを認証組織の範囲で取得する。"""
    return db.query(
        "operations/metrics/sql/events_get.sql",
        {"organization_id": organization_id, "id": id},
        EventsRow,
    )


def events_insert(db: Database, row: EventsRow) -> int:
    """eventsの型検査済み行を保存する。"""
    return db.execute("operations/metrics/sql/events_insert.sql", row.model_dump())


def events_list(db: Database, organization_id: str) -> list[EventsRow]:
    """eventsを認証組織の範囲で取得する。"""
    return db.query(
        "operations/metrics/sql/events_list.sql", {"organization_id": organization_id}, EventsRow
    )


def submissions_delete(db: Database, organization_id: str, id: str) -> int:
    """submissionsの指定行だけを削除する。"""
    return db.execute(
        "operations/reviews/sql/submissions_delete.sql",
        {"organization_id": organization_id, "id": id},
    )


def submissions_get(db: Database, organization_id: str, id: str) -> list[SubmissionsRow]:
    """submissionsを認証組織の範囲で取得する。"""
    return db.query(
        "operations/reviews/sql/submissions_get.sql",
        {"organization_id": organization_id, "id": id},
        SubmissionsRow,
    )


def submissions_insert(db: Database, row: SubmissionsRow) -> int:
    """submissionsの型検査済み行を保存する。"""
    return db.execute("operations/reviews/sql/submissions_insert.sql", row.model_dump())


def submissions_list(db: Database, organization_id: str) -> list[SubmissionsRow]:
    """submissionsを認証組織の範囲で取得する。"""
    return db.query(
        "operations/reviews/sql/submissions_list.sql",
        {"organization_id": organization_id},
        SubmissionsRow,
    )


def submissions_update(db: Database, row: SubmissionsRow) -> int:
    """submissionsの型検査済み行を保存する。"""
    return db.execute("operations/reviews/sql/submissions_update.sql", row.model_dump())


def audit_get(db: Database, organization_id: str, id: str) -> list[AuditRow]:
    """auditを認証組織の範囲で取得する。"""
    return db.query(
        "operations/system/sql/audit_get.sql",
        {"organization_id": organization_id, "id": id},
        AuditRow,
    )


def audit_insert(db: Database, row: AuditRow) -> int:
    """auditの型検査済み行を保存する。"""
    return db.execute("operations/system/sql/audit_insert.sql", row.model_dump())


def audit_list(db: Database, organization_id: str) -> list[AuditRow]:
    """auditを認証組織の範囲で取得する。"""
    return db.query(
        "operations/system/sql/audit_list.sql", {"organization_id": organization_id}, AuditRow
    )


def idempotency_get(db: Database, organization_id: str, id: str) -> list[IdempotencyRow]:
    """idempotencyを認証組織の範囲で取得する。"""
    return db.query(
        "operations/system/sql/idempotency_get.sql",
        {"organization_id": organization_id, "id": id},
        IdempotencyRow,
    )


def idempotency_insert(db: Database, row: IdempotencyRow) -> int:
    """idempotencyの型検査済み行を保存する。"""
    return db.execute("operations/system/sql/idempotency_insert.sql", row.model_dump())


def idempotency_list(db: Database, organization_id: str) -> list[IdempotencyRow]:
    """idempotencyを認証組織の範囲で取得する。"""
    return db.query(
        "operations/system/sql/idempotency_list.sql",
        {"organization_id": organization_id},
        IdempotencyRow,
    )
