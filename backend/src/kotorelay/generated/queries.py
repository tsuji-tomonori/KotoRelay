"""DDL・SQLから生成した型付き境界。直接編集しない。
SHA256: 2b3b7e49d1fdb24125431d989878de6a2e939657d28e6d7ec81192377735a645
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
    "現在の組織に属する指定の回答履歴の記録を削除する。"
    return db.execute(
        "operations/chat/sql/answers_delete.sql", {"organization_id": organization_id, "id": id}
    )


def answers_get(db: Database, organization_id: str, id: str) -> list[AnswersRow]:
    "現在の組織に属する指定の回答履歴について、質問・回答の保存先と根拠・回答状態を取得する。"
    return db.query(
        "operations/chat/sql/answers_get.sql",
        {"organization_id": organization_id, "id": id},
        AnswersRow,
    )


def answers_insert(db: Database, row: AnswersRow) -> int:
    "現在の組織の回答履歴として、質問者・利用部署・質問と回答の保存先・根拠を登録する。"
    return db.execute("operations/chat/sql/answers_insert.sql", row.model_dump())


def answers_list(db: Database, organization_id: str) -> list[AnswersRow]:
    "現在の組織に属する回答履歴を識別子順に一覧取得する。"
    return db.query(
        "operations/chat/sql/answers_list.sql", {"organization_id": organization_id}, AnswersRow
    )


def answers_update(db: Database, row: AnswersRow) -> int:
    "現在の組織に属する指定の回答履歴について、質問・回答の保存先と根拠・回答状態を更新する。"
    return db.execute("operations/chat/sql/answers_update.sql", row.model_dump())


def conversations_delete(db: Database, organization_id: str, id: str) -> int:
    "現在の組織に属する指定の会話の記録を削除する。"
    return db.execute(
        "operations/chat/sql/conversations_delete.sql",
        {"organization_id": organization_id, "id": id},
    )


def conversations_get(db: Database, organization_id: str, id: str) -> list[ConversationsRow]:
    "現在の組織に属する指定の会話について、会話の所有者と開始日時を取得する。"
    return db.query(
        "operations/chat/sql/conversations_get.sql",
        {"organization_id": organization_id, "id": id},
        ConversationsRow,
    )


def conversations_insert(db: Database, row: ConversationsRow) -> int:
    "現在の組織の会話を、所有者と開始日時を指定して登録する。"
    return db.execute("operations/chat/sql/conversations_insert.sql", row.model_dump())


def conversations_list(db: Database, organization_id: str) -> list[ConversationsRow]:
    "現在の組織に属する会話を識別子順に一覧取得する。"
    return db.query(
        "operations/chat/sql/conversations_list.sql",
        {"organization_id": organization_id},
        ConversationsRow,
    )


def conversations_update(db: Database, row: ConversationsRow) -> int:
    "現在の組織に属する指定の会話について、会話の所有者と開始日時を更新する。"
    return db.execute("operations/chat/sql/conversations_update.sql", row.model_dump())


def documents_by_department(
    db: Database, organization_id: str, department_id: str
) -> list[DocumentsRow]:
    "現在の組織に属する文書を指定した所有部署で絞り込み、一覧の対象を取得する。"
    return db.query(
        "operations/documents/sql/documents_by_department.sql",
        {"organization_id": organization_id, "department_id": department_id},
        DocumentsRow,
    )


def documents_delete(db: Database, organization_id: str, id: str) -> int:
    "現在の組織に属する指定の文書の記録を削除する。"
    return db.execute(
        "operations/documents/sql/documents_delete.sql",
        {"organization_id": organization_id, "id": id},
    )


def documents_get(db: Database, organization_id: str, id: str) -> list[DocumentsRow]:
    "現在の組織に属する指定の文書について、文書の所有部署・公開範囲・状態・公開版の参照を取得する。"
    return db.query(
        "operations/documents/sql/documents_get.sql",
        {"organization_id": organization_id, "id": id},
        DocumentsRow,
    )


def documents_insert(db: Database, row: DocumentsRow) -> int:
    "現在の組織の文書を、所有部署・公開範囲・状態を指定して登録する。"
    return db.execute("operations/documents/sql/documents_insert.sql", row.model_dump())


def documents_list(db: Database, organization_id: str) -> list[DocumentsRow]:
    "現在の組織に属する文書を識別子順に一覧取得する。"
    return db.query(
        "operations/documents/sql/documents_list.sql",
        {"organization_id": organization_id},
        DocumentsRow,
    )


def documents_update(db: Database, row: DocumentsRow) -> int:
    "現在の組織に属する指定の文書について、文書の所有部署・公開範囲・状態・公開版の参照を更新する。"
    return db.execute("operations/documents/sql/documents_update.sql", row.model_dump())


def drafts_delete(db: Database, organization_id: str, id: str) -> int:
    "現在の組織に属する指定の下書きの記録を削除する。"
    return db.execute(
        "operations/documents/sql/drafts_delete.sql", {"organization_id": organization_id, "id": id}
    )


def drafts_get(db: Database, organization_id: str, id: str) -> list[DraftsRow]:
    "現在の組織に属する指定の下書きについて、本文の保存先・画像配置・改訂番号を取得する。"
    return db.query(
        "operations/documents/sql/drafts_get.sql",
        {"organization_id": organization_id, "id": id},
        DraftsRow,
    )


def drafts_insert(db: Database, row: DraftsRow) -> int:
    "現在の組織の文書の下書きを、本文の保存先・画像配置・改訂番号を指定して登録する。"
    return db.execute("operations/documents/sql/drafts_insert.sql", row.model_dump())


def drafts_list(db: Database, organization_id: str) -> list[DraftsRow]:
    "現在の組織に属する下書きを識別子順に一覧取得する。"
    return db.query(
        "operations/documents/sql/drafts_list.sql", {"organization_id": organization_id}, DraftsRow
    )


def drafts_update(db: Database, row: DraftsRow) -> int:
    "現在の組織に属する指定の下書きについて、本文の保存先・画像配置・改訂番号を更新する。"
    return db.execute("operations/documents/sql/drafts_update.sql", row.model_dump())


def versions_delete(db: Database, organization_id: str, id: str) -> int:
    "現在の組織に属する指定の文書版の記録を削除する。"
    return db.execute(
        "operations/documents/sql/versions_delete.sql",
        {"organization_id": organization_id, "id": id},
    )


def versions_get(db: Database, organization_id: str, id: str) -> list[VersionsRow]:
    "現在の組織に属する指定の文書版について、確定した本文の保存先と画像構成・検証用ハッシュを取得する。"
    return db.query(
        "operations/documents/sql/versions_get.sql",
        {"organization_id": organization_id, "id": id},
        VersionsRow,
    )


def versions_insert(db: Database, row: VersionsRow) -> int:
    "現在の組織の文書版を、版番号・本文の保存先・画像構成・検証用ハッシュを指定して登録する。"
    return db.execute("operations/documents/sql/versions_insert.sql", row.model_dump())


def versions_list(db: Database, organization_id: str) -> list[VersionsRow]:
    "現在の組織に属する文書版を識別子順に一覧取得する。"
    return db.query(
        "operations/documents/sql/versions_list.sql",
        {"organization_id": organization_id},
        VersionsRow,
    )


def departments_get(db: Database, organization_id: str, id: str) -> list[DepartmentsRow]:
    "現在の組織に属する指定の部署について、部署名と有効状態を取得する。"
    return db.query(
        "operations/groups/sql/departments_get.sql",
        {"organization_id": organization_id, "id": id},
        DepartmentsRow,
    )


def departments_insert(db: Database, row: DepartmentsRow) -> int:
    "現在の組織の部署を、部署名と有効状態を指定して登録する。"
    return db.execute("operations/groups/sql/departments_insert.sql", row.model_dump())


def departments_list(db: Database, organization_id: str) -> list[DepartmentsRow]:
    "現在の組織に属する部署を識別子順に一覧取得する。"
    return db.query(
        "operations/groups/sql/departments_list.sql",
        {"organization_id": organization_id},
        DepartmentsRow,
    )


def departments_update(db: Database, row: DepartmentsRow) -> int:
    "現在の組織に属する指定の部署について、部署名と有効状態を更新する。"
    return db.execute("operations/groups/sql/departments_update.sql", row.model_dump())


def memberships_delete(db: Database, organization_id: str, id: str) -> int:
    "現在の組織に属する指定の部署所属の記録を削除する。"
    return db.execute(
        "operations/groups/sql/memberships_delete.sql",
        {"organization_id": organization_id, "id": id},
    )


def memberships_get(db: Database, organization_id: str, id: str) -> list[MembershipsRow]:
    "現在の組織に属する指定の部署所属について、所属部署・利用者・執筆や審査の権限・有効状態を取得する。"
    return db.query(
        "operations/groups/sql/memberships_get.sql",
        {"organization_id": organization_id, "id": id},
        MembershipsRow,
    )


def memberships_insert(db: Database, row: MembershipsRow) -> int:
    "現在の組織の利用者の部署所属を、所属部署・権限・有効状態を指定して登録する。"
    return db.execute("operations/groups/sql/memberships_insert.sql", row.model_dump())


def memberships_list(db: Database, organization_id: str) -> list[MembershipsRow]:
    "現在の組織に属する部署所属を識別子順に一覧取得する。"
    return db.query(
        "operations/groups/sql/memberships_list.sql",
        {"organization_id": organization_id},
        MembershipsRow,
    )


def memberships_update(db: Database, row: MembershipsRow) -> int:
    "現在の組織に属する指定の部署所属について、所属部署・利用者・執筆や審査の権限・有効状態を更新する。"
    return db.execute("operations/groups/sql/memberships_update.sql", row.model_dump())


def organizations_fence(db: Database, row: OrganizationsRow) -> int:
    "組織の改訂番号が一致する場合だけ番号を進め、認可判定と権限失効の競合を検出する。"
    return db.execute("operations/identity/sql/organizations_fence.sql", row.model_dump())


def organizations_get(db: Database, organization_id: str, id: str) -> list[OrganizationsRow]:
    "現在の組織の組織名・改訂番号・利用停止状態を取得する。"
    return db.query(
        "operations/identity/sql/organizations_get.sql",
        {"organization_id": organization_id, "id": id},
        OrganizationsRow,
    )


def organizations_insert(db: Database, row: OrganizationsRow) -> int:
    "組織を、組織名・改訂番号・利用停止状態を指定して登録する。"
    return db.execute("operations/identity/sql/organizations_insert.sql", row.model_dump())


def organizations_list(db: Database, organization_id: str) -> list[OrganizationsRow]:
    "現在の組織に一致する組織レコードを識別子順に一覧取得する。"
    return db.query(
        "operations/identity/sql/organizations_list.sql",
        {"organization_id": organization_id},
        OrganizationsRow,
    )


def organizations_update(db: Database, row: OrganizationsRow) -> int:
    "現在の組織の組織名・改訂番号・利用停止状態を更新する。"
    return db.execute("operations/identity/sql/organizations_update.sql", row.model_dump())


def users_get(db: Database, organization_id: str, id: str) -> list[UsersRow]:
    "現在の組織に属する指定の利用者について、認証主体・表示名・有効状態・運用権限を取得する。"
    return db.query(
        "operations/identity/sql/users_get.sql",
        {"organization_id": organization_id, "id": id},
        UsersRow,
    )


def users_insert(db: Database, row: UsersRow) -> int:
    "現在の組織の利用者を、認証主体・表示名・有効状態・運用権限を指定して登録する。"
    return db.execute("operations/identity/sql/users_insert.sql", row.model_dump())


def users_list(db: Database, organization_id: str) -> list[UsersRow]:
    "現在の組織に属する利用者を識別子順に一覧取得する。"
    return db.query(
        "operations/identity/sql/users_list.sql", {"organization_id": organization_id}, UsersRow
    )


def users_update(db: Database, row: UsersRow) -> int:
    "現在の組織に属する指定の利用者について、認証主体・表示名・有効状態・運用権限を更新する。"
    return db.execute("operations/identity/sql/users_update.sql", row.model_dump())


def assets_delete(db: Database, organization_id: str, id: str) -> int:
    "現在の組織に属する指定の添付画像の記録を削除する。"
    return db.execute(
        "operations/images/sql/assets_delete.sql", {"organization_id": organization_id, "id": id}
    )


def assets_get(db: Database, organization_id: str, id: str) -> list[AssetsRow]:
    "現在の組織に属する指定の添付画像について、画像の保存先・形式・寸法・検証用ハッシュを取得する。"
    return db.query(
        "operations/images/sql/assets_get.sql",
        {"organization_id": organization_id, "id": id},
        AssetsRow,
    )


def assets_insert(db: Database, row: AssetsRow) -> int:
    "現在の組織の文書に添付した画像の保存先・形式・寸法・検証用ハッシュを登録する。"
    return db.execute("operations/images/sql/assets_insert.sql", row.model_dump())


def assets_list(db: Database, organization_id: str) -> list[AssetsRow]:
    "現在の組織に属する添付画像を識別子順に一覧取得する。"
    return db.query(
        "operations/images/sql/assets_list.sql", {"organization_id": organization_id}, AssetsRow
    )


def ocr_runs_delete(db: Database, organization_id: str, id: str) -> int:
    "現在の組織に属する指定の文字認識の実行記録の記録を削除する。"
    return db.execute(
        "operations/images/sql/ocr_runs_delete.sql", {"organization_id": organization_id, "id": id}
    )


def ocr_runs_get(db: Database, organization_id: str, id: str) -> list[OcrRunsRow]:
    "現在の組織に属する指定の文字認識の実行記録について、認識結果の保存先・検証用ハッシュ・確認状態を取得する。"
    return db.query(
        "operations/images/sql/ocr_runs_get.sql",
        {"organization_id": organization_id, "id": id},
        OcrRunsRow,
    )


def ocr_runs_insert(db: Database, row: OcrRunsRow) -> int:
    "現在の組織の画像に対する文字認識の実行記録を、認識結果の保存先・検証用ハッシュ・確認状態とともに登録する。"
    return db.execute("operations/images/sql/ocr_runs_insert.sql", row.model_dump())


def ocr_runs_list(db: Database, organization_id: str) -> list[OcrRunsRow]:
    "現在の組織に属する文字認識の実行記録を識別子順に一覧取得する。"
    return db.query(
        "operations/images/sql/ocr_runs_list.sql", {"organization_id": organization_id}, OcrRunsRow
    )


def chunks_delete(db: Database, organization_id: str, id: str) -> int:
    "現在の組織に属する指定の検索用の文書断片の記録を削除する。"
    return db.execute(
        "operations/indexing/sql/chunks_delete.sql", {"organization_id": organization_id, "id": id}
    )


def chunks_get(db: Database, organization_id: str, id: str) -> list[ChunksRow]:
    "現在の組織に属する指定の検索用の文書断片について、本文の保存先・出典の版・画像配置・索引反映状態を取得する。"
    return db.query(
        "operations/indexing/sql/chunks_get.sql",
        {"organization_id": organization_id, "id": id},
        ChunksRow,
    )


def chunks_insert(db: Database, row: ChunksRow) -> int:
    "現在の組織の検索用の文書断片を、出典の版・本文の保存先・画像配置とともに登録する。"
    return db.execute("operations/indexing/sql/chunks_insert.sql", row.model_dump())


def chunks_list(db: Database, organization_id: str) -> list[ChunksRow]:
    "現在の組織に属する検索用の文書断片を識別子順に一覧取得する。"
    return db.query(
        "operations/indexing/sql/chunks_list.sql", {"organization_id": organization_id}, ChunksRow
    )


def chunks_update(db: Database, row: ChunksRow) -> int:
    "現在の組織に属する指定の検索用の文書断片について、本文の保存先・出典の版・画像配置・索引反映状態を更新する。"
    return db.execute("operations/indexing/sql/chunks_update.sql", row.model_dump())


def outbox_delete(db: Database, organization_id: str, id: str) -> int:
    "現在の組織に属する指定の反映・削除ジョブの記録を削除する。"
    return db.execute(
        "operations/indexing/sql/outbox_delete.sql", {"organization_id": organization_id, "id": id}
    )


def outbox_get(db: Database, organization_id: str, id: str) -> list[OutboxRow]:
    "現在の組織に属する指定の反映・削除ジョブについて、対象文書と版・処理種別・進行状態・試行回数を取得する。"
    return db.query(
        "operations/indexing/sql/outbox_get.sql",
        {"organization_id": organization_id, "id": id},
        OutboxRow,
    )


def outbox_insert(db: Database, row: OutboxRow) -> int:
    "現在の組織の反映・削除ジョブを、対象文書と版・処理種別を指定して登録する。"
    return db.execute("operations/indexing/sql/outbox_insert.sql", row.model_dump())


def outbox_list(db: Database, organization_id: str) -> list[OutboxRow]:
    "現在の組織に属する反映・削除ジョブを識別子順に一覧取得する。"
    return db.query(
        "operations/indexing/sql/outbox_list.sql", {"organization_id": organization_id}, OutboxRow
    )


def outbox_update(db: Database, row: OutboxRow) -> int:
    "現在の組織に属する指定の反映・削除ジョブについて、対象文書と版・処理種別・進行状態・試行回数を更新する。"
    return db.execute("operations/indexing/sql/outbox_update.sql", row.model_dump())


def events_get(db: Database, organization_id: str, id: str) -> list[EventsRow]:
    "現在の組織に属する指定の利用イベントについて、利用者・帰属部署・閲覧や質問の対象・結果・発生日時を取得する。"
    return db.query(
        "operations/metrics/sql/events_get.sql",
        {"organization_id": organization_id, "id": id},
        EventsRow,
    )


def events_insert(db: Database, row: EventsRow) -> int:
    "現在の組織の利用イベントとして、利用者・帰属部署・閲覧や質問の対象・結果・発生日時を登録する。"
    return db.execute("operations/metrics/sql/events_insert.sql", row.model_dump())


def events_list(db: Database, organization_id: str) -> list[EventsRow]:
    "現在の組織に属する利用イベントを識別子順に一覧取得する。"
    return db.query(
        "operations/metrics/sql/events_list.sql", {"organization_id": organization_id}, EventsRow
    )


def submissions_delete(db: Database, organization_id: str, id: str) -> int:
    "現在の組織に属する指定の承認申請の記録を削除する。"
    return db.execute(
        "operations/reviews/sql/submissions_delete.sql",
        {"organization_id": organization_id, "id": id},
    )


def submissions_get(db: Database, organization_id: str, id: str) -> list[SubmissionsRow]:
    "現在の組織に属する指定の承認申請について、対象の文書版・審査状態・判断者・理由を取得する。"
    return db.query(
        "operations/reviews/sql/submissions_get.sql",
        {"organization_id": organization_id, "id": id},
        SubmissionsRow,
    )


def submissions_insert(db: Database, row: SubmissionsRow) -> int:
    "現在の組織の承認申請を、対象の文書版・申請者・審査状態・検証用ハッシュとともに登録する。"
    return db.execute("operations/reviews/sql/submissions_insert.sql", row.model_dump())


def submissions_list(db: Database, organization_id: str) -> list[SubmissionsRow]:
    "現在の組織に属する承認申請を識別子順に一覧取得する。"
    return db.query(
        "operations/reviews/sql/submissions_list.sql",
        {"organization_id": organization_id},
        SubmissionsRow,
    )


def submissions_update(db: Database, row: SubmissionsRow) -> int:
    "現在の組織に属する指定の承認申請について、対象の文書版・審査状態・判断者・理由を更新する。"
    return db.execute("operations/reviews/sql/submissions_update.sql", row.model_dump())


def audit_get(db: Database, organization_id: str, id: str) -> list[AuditRow]:
    "現在の組織に属する指定の監査記録について、操作した利用者・対象・変更前後の状態・理由を取得する。"
    return db.query(
        "operations/system/sql/audit_get.sql",
        {"organization_id": organization_id, "id": id},
        AuditRow,
    )


def audit_insert(db: Database, row: AuditRow) -> int:
    "現在の組織の監査記録として、操作した利用者・対象・変更前後の状態・理由を登録する。"
    return db.execute("operations/system/sql/audit_insert.sql", row.model_dump())


def audit_list(db: Database, organization_id: str) -> list[AuditRow]:
    "現在の組織に属する監査記録を識別子順に一覧取得する。"
    return db.query(
        "operations/system/sql/audit_list.sql", {"organization_id": organization_id}, AuditRow
    )


def idempotency_get(db: Database, organization_id: str, id: str) -> list[IdempotencyRow]:
    "現在の組織に属する指定の再送判定の記録について、実行済み操作の入力ハッシュと応答を取得する。"
    return db.query(
        "operations/system/sql/idempotency_get.sql",
        {"organization_id": organization_id, "id": id},
        IdempotencyRow,
    )


def idempotency_insert(db: Database, row: IdempotencyRow) -> int:
    "現在の組織の操作の再送を判定するため、実行済み操作の入力ハッシュと応答を登録する。"
    return db.execute("operations/system/sql/idempotency_insert.sql", row.model_dump())


def idempotency_list(db: Database, organization_id: str) -> list[IdempotencyRow]:
    "現在の組織に属する再送判定の記録を識別子順に一覧取得する。"
    return db.query(
        "operations/system/sql/idempotency_list.sql",
        {"organization_id": organization_id},
        IdempotencyRow,
    )
