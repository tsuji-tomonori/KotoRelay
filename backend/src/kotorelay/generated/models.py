"""DDL・SQLから生成した型付き境界。直接編集しない。
SHA256: 412374d70ba7e32ec1bb4eb3a693723541647d80e4d8587b9ff0485c908d3579
"""

from datetime import datetime

from pydantic import BaseModel


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
