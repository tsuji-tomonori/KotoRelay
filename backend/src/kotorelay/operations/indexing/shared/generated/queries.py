"""DDL・SQLから生成した型付き境界。直接編集しない。
SHA256: 50dbba107dd6935d5879f05f19e78ce01fe4d6aec3191780cc061e24fa250f14
"""

from datetime import datetime

from pydantic import BaseModel, ConfigDict

from kotorelay.db import Database
from kotorelay.generated.models import (
    AnswersRow,
    AssetsRow,
    ChunksRow,
    DocumentsRow,
    DraftsRow,
    OcrRunsRow,
    OutboxRow,
    VersionsRow,
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
        "operations/indexing/shared/sql/001_answers_list.sql", params.model_dump(), AnswersListRow
    )


class AssetsDeleteParams(BaseModel):
    """assets_deleteの束縛引数。SQLで使用する項目だけを受け付ける。"""

    model_config = ConfigDict(extra="forbid")
    organization_id: str
    id: str


def assets_delete(db: Database, params: AssetsDeleteParams) -> int:
    "現在の組織に属する指定の添付画像の記録を削除する。"
    return db.execute("operations/indexing/shared/sql/002_assets_delete.sql", params.model_dump())


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
        "operations/indexing/shared/sql/003_assets_get.sql", params.model_dump(), AssetsGetRow
    )


class AssetsListParams(BaseModel):
    """assets_listの束縛引数。SQLで使用する項目だけを受け付ける。"""

    model_config = ConfigDict(extra="forbid")
    organization_id: str


class AssetsListRow(AssetsRow):
    """assets_listのSELECT句に対応する取得行。"""

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


def assets_list(db: Database, params: AssetsListParams) -> list[AssetsListRow]:
    "現在の組織に属する添付画像を識別子順に一覧取得する。"
    return db.query(
        "operations/indexing/shared/sql/004_assets_list.sql", params.model_dump(), AssetsListRow
    )


class ChunksDeleteParams(BaseModel):
    """chunks_deleteの束縛引数。SQLで使用する項目だけを受け付ける。"""

    model_config = ConfigDict(extra="forbid")
    organization_id: str
    id: str


def chunks_delete(db: Database, params: ChunksDeleteParams) -> int:
    "現在の組織に属する指定の検索用の文書断片の記録を削除する。"
    return db.execute("operations/indexing/shared/sql/005_chunks_delete.sql", params.model_dump())


class ChunksInsertParams(BaseModel):
    """chunks_insertの束縛引数。SQLで使用する項目だけを受け付ける。"""

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


def chunks_insert(db: Database, params: ChunksInsertParams) -> int:
    "現在の組織の検索用の文書断片を、出典の版・本文の保存先・画像配置とともに登録する。"
    return db.execute("operations/indexing/shared/sql/006_chunks_insert.sql", params.model_dump())


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
        "operations/indexing/shared/sql/007_chunks_list.sql", params.model_dump(), ChunksListRow
    )


class ChunksUpdateParams(BaseModel):
    """chunks_updateの束縛引数。SQLで使用する項目だけを受け付ける。"""

    model_config = ConfigDict(extra="forbid")
    document_id: str
    version_id: str
    body_key: str
    sha256: str
    heading: str
    placements: str
    manifest_hash: str
    ready: bool
    organization_id: str
    id: str


def chunks_update(db: Database, params: ChunksUpdateParams) -> int:
    "現在の組織に属する指定の検索用の文書断片について、本文の保存先・出典の版・画像配置・索引反映状態を更新する。"
    return db.execute("operations/indexing/shared/sql/008_chunks_update.sql", params.model_dump())


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
        "operations/indexing/shared/sql/009_documents_get.sql", params.model_dump(), DocumentsGetRow
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
        "operations/indexing/shared/sql/010_documents_list.sql",
        params.model_dump(),
        DocumentsListRow,
    )


class DraftsDeleteParams(BaseModel):
    """drafts_deleteの束縛引数。SQLで使用する項目だけを受け付ける。"""

    model_config = ConfigDict(extra="forbid")
    organization_id: str
    id: str


def drafts_delete(db: Database, params: DraftsDeleteParams) -> int:
    "現在の組織に属する指定の下書きの記録を削除する。"
    return db.execute("operations/indexing/shared/sql/011_drafts_delete.sql", params.model_dump())


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
        "operations/indexing/shared/sql/012_drafts_list.sql", params.model_dump(), DraftsListRow
    )


class OcrRunsDeleteParams(BaseModel):
    """ocr_runs_deleteの束縛引数。SQLで使用する項目だけを受け付ける。"""

    model_config = ConfigDict(extra="forbid")
    organization_id: str
    id: str


def ocr_runs_delete(db: Database, params: OcrRunsDeleteParams) -> int:
    "現在の組織に属する指定の文字認識の実行記録の記録を削除する。"
    return db.execute("operations/indexing/shared/sql/013_ocr_runs_delete.sql", params.model_dump())


class OcrRunsGetParams(BaseModel):
    """ocr_runs_getの束縛引数。SQLで使用する項目だけを受け付ける。"""

    model_config = ConfigDict(extra="forbid")
    organization_id: str
    id: str


class OcrRunsGetRow(OcrRunsRow):
    """ocr_runs_getのSELECT句に対応する取得行。"""

    model_config = ConfigDict(extra="forbid")
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


def ocr_runs_get(db: Database, params: OcrRunsGetParams) -> list[OcrRunsGetRow]:
    "現在の組織に属する指定の文字認識の実行記録について、認識結果の保存先・検証用ハッシュ・確認状態を取得する。"
    return db.query(
        "operations/indexing/shared/sql/014_ocr_runs_get.sql", params.model_dump(), OcrRunsGetRow
    )


class OcrRunsListParams(BaseModel):
    """ocr_runs_listの束縛引数。SQLで使用する項目だけを受け付ける。"""

    model_config = ConfigDict(extra="forbid")
    organization_id: str


class OcrRunsListRow(OcrRunsRow):
    """ocr_runs_listのSELECT句に対応する取得行。"""

    model_config = ConfigDict(extra="forbid")
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


def ocr_runs_list(db: Database, params: OcrRunsListParams) -> list[OcrRunsListRow]:
    "現在の組織に属する文字認識の実行記録を識別子順に一覧取得する。"
    return db.query(
        "operations/indexing/shared/sql/015_ocr_runs_list.sql", params.model_dump(), OcrRunsListRow
    )


class OutboxGetParams(BaseModel):
    """outbox_getの束縛引数。SQLで使用する項目だけを受け付ける。"""

    model_config = ConfigDict(extra="forbid")
    organization_id: str
    id: str


class OutboxGetRow(OutboxRow):
    """outbox_getのSELECT句に対応する取得行。"""

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


def outbox_get(db: Database, params: OutboxGetParams) -> list[OutboxGetRow]:
    "現在の組織に属する指定の反映・削除ジョブについて、対象文書と版・処理種別・進行状態・試行回数を取得する。"
    return db.query(
        "operations/indexing/shared/sql/016_outbox_get.sql", params.model_dump(), OutboxGetRow
    )


class OutboxUpdateParams(BaseModel):
    """outbox_updateの束縛引数。SQLで使用する項目だけを受け付ける。"""

    model_config = ConfigDict(extra="forbid")
    document_id: str
    version_id: str | None
    kind: str
    status: str
    attempts: int
    error_code: str
    created_at: datetime
    organization_id: str
    id: str


def outbox_update(db: Database, params: OutboxUpdateParams) -> int:
    "現在の組織に属する指定の反映・削除ジョブについて、対象文書と版・処理種別・進行状態・試行回数を更新する。"
    return db.execute("operations/indexing/shared/sql/017_outbox_update.sql", params.model_dump())


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
        "operations/indexing/shared/sql/018_versions_get.sql", params.model_dump(), VersionsGetRow
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
        "operations/indexing/shared/sql/019_versions_list.sql", params.model_dump(), VersionsListRow
    )
