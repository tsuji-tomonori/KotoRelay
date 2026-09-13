"""DDL・SQLから生成した型付き境界。直接編集しない。
SHA256: 23563c43e5278a00671ddf3eadd51598430e9e42620a1085bb8df8dd3023e2c4
"""

from datetime import datetime

from pydantic import BaseModel, ConfigDict

from kotorelay.db import Database
from kotorelay.generated.models import (
    AnswersRow,
    AssetsRow,
    ChunksRow,
    ConversationsRow,
    DocumentsRow,
    EventsRow,
    VersionsRow,
)


class AnswersGetParams(BaseModel):
    """answers_getの束縛引数。SQLで使用する項目だけを受け付ける。"""

    model_config = ConfigDict(extra="forbid")
    organization_id: str
    id: str


class AnswersGetRow(AnswersRow):
    """answers_getのSELECT句に対応する取得行。"""

    model_config = ConfigDict(extra="forbid")
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


def answers_get(db: Database, params: AnswersGetParams) -> list[AnswersGetRow]:
    "現在の組織に属する指定の回答履歴について、質問・回答の保存先と根拠・回答状態を取得する。"
    return db.query(
        "operations/chat/ask_question/sql/001_answers_get.sql", params.model_dump(), AnswersGetRow
    )


class AnswersInsertParams(BaseModel):
    """answers_insertの束縛引数。SQLで使用する項目だけを受け付ける。"""

    model_config = ConfigDict(extra="forbid")
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


def answers_insert(db: Database, params: AnswersInsertParams) -> int:
    "現在の組織の回答履歴として、質問者・利用部署・質問と回答の保存先・根拠を登録する。"
    return db.execute(
        "operations/chat/ask_question/sql/002_answers_insert.sql", params.model_dump()
    )


class AnswersListParams(BaseModel):
    """answers_listの束縛引数。SQLで使用する項目だけを受け付ける。"""

    model_config = ConfigDict(extra="forbid")
    organization_id: str


class AnswersListRow(AnswersRow):
    """answers_listのSELECT句に対応する取得行。"""

    model_config = ConfigDict(extra="forbid")
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


def answers_list(db: Database, params: AnswersListParams) -> list[AnswersListRow]:
    "現在の組織に属する回答履歴を識別子順に一覧取得する。"
    return db.query(
        "operations/chat/ask_question/sql/003_answers_list.sql", params.model_dump(), AnswersListRow
    )


class AssetsGetParams(BaseModel):
    """assets_getの束縛引数。SQLで使用する項目だけを受け付ける。"""

    model_config = ConfigDict(extra="forbid")
    organization_id: str
    id: str


class AssetsGetRow(AssetsRow):
    """assets_getのSELECT句に対応する取得行。"""

    model_config = ConfigDict(extra="forbid")
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


def assets_get(db: Database, params: AssetsGetParams) -> list[AssetsGetRow]:
    "現在の組織に属する指定の添付画像について、画像の保存先・形式・寸法・検証用ハッシュを取得する。"
    return db.query(
        "operations/chat/ask_question/sql/004_assets_get.sql", params.model_dump(), AssetsGetRow
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
        "operations/chat/ask_question/sql/005_chunks_list.sql", params.model_dump(), ChunksListRow
    )


class ConversationsGetParams(BaseModel):
    """conversations_getの束縛引数。SQLで使用する項目だけを受け付ける。"""

    model_config = ConfigDict(extra="forbid")
    organization_id: str
    id: str


class ConversationsGetRow(ConversationsRow):
    """conversations_getのSELECT句に対応する取得行。"""

    model_config = ConfigDict(extra="forbid")
    id: str
    organization_id: str
    user_id: str
    created_at: datetime


def conversations_get(db: Database, params: ConversationsGetParams) -> list[ConversationsGetRow]:
    "現在の組織に属する指定の会話について、会話の所有者と開始日時を取得する。"
    return db.query(
        "operations/chat/ask_question/sql/006_conversations_get.sql",
        params.model_dump(),
        ConversationsGetRow,
    )


class ConversationsInsertParams(BaseModel):
    """conversations_insertの束縛引数。SQLで使用する項目だけを受け付ける。"""

    model_config = ConfigDict(extra="forbid")
    id: str
    organization_id: str
    user_id: str
    created_at: datetime


def conversations_insert(db: Database, params: ConversationsInsertParams) -> int:
    "現在の組織の会話を、所有者と開始日時を指定して登録する。"
    return db.execute(
        "operations/chat/ask_question/sql/007_conversations_insert.sql", params.model_dump()
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
        "operations/chat/ask_question/sql/008_documents_list.sql",
        params.model_dump(),
        DocumentsListRow,
    )


class EventsInsertParams(BaseModel):
    """events_insertの束縛引数。SQLで使用する項目だけを受け付ける。"""

    model_config = ConfigDict(extra="forbid")
    id: str
    organization_id: str
    user_id: str
    department_id: str
    document_id: str | None
    answer_id: str | None
    kind: str
    outcome: str
    created_at: datetime


def events_insert(db: Database, params: EventsInsertParams) -> int:
    "現在の組織の利用イベントとして、利用者・帰属部署・閲覧や質問の対象・結果・発生日時を登録する。"
    return db.execute("operations/chat/ask_question/sql/009_events_insert.sql", params.model_dump())


class EventsListParams(BaseModel):
    """events_listの束縛引数。SQLで使用する項目だけを受け付ける。"""

    model_config = ConfigDict(extra="forbid")
    organization_id: str


class EventsListRow(EventsRow):
    """events_listのSELECT句に対応する取得行。"""

    model_config = ConfigDict(extra="forbid")
    id: str
    organization_id: str
    user_id: str
    department_id: str
    document_id: str | None
    answer_id: str | None
    kind: str
    outcome: str
    created_at: datetime


def events_list(db: Database, params: EventsListParams) -> list[EventsListRow]:
    "現在の組織に属する利用イベントを識別子順に一覧取得する。"
    return db.query(
        "operations/chat/ask_question/sql/010_events_list.sql", params.model_dump(), EventsListRow
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
        "operations/chat/ask_question/sql/011_versions_get.sql", params.model_dump(), VersionsGetRow
    )
