"""DDL・SQLから生成した型付き境界。直接編集しない。
SHA256: 7e39b557835d0756a7dbd5ccc793d2378fa557913daf20185611845ed608baaa
"""

from datetime import datetime

from pydantic import BaseModel, ConfigDict

from kotorelay.db import Database
from kotorelay.generated.models import (
    AssetsRow,
    DraftsRow,
    OcrRunsRow,
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
        "operations/documents/submit_version/sql/001_assets_get.sql",
        params.model_dump(),
        AssetsGetRow,
    )


class DocumentsUpdateParams(BaseModel):
    """documents_updateの束縛引数。SQLで使用する項目だけを受け付ける。"""

    model_config = ConfigDict(extra="forbid")
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
    organization_id: str
    id: str


def documents_update(db: Database, params: DocumentsUpdateParams) -> int:
    "現在の組織に属する指定の文書について、文書の所有部署・公開範囲・状態・公開版の参照を更新する。"
    return db.execute(
        "operations/documents/submit_version/sql/002_documents_update.sql", params.model_dump()
    )


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
        "operations/documents/submit_version/sql/003_drafts_list.sql",
        params.model_dump(),
        DraftsListRow,
    )


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
        "operations/documents/submit_version/sql/004_ocr_runs_get.sql",
        params.model_dump(),
        OcrRunsGetRow,
    )


class SubmissionsInsertParams(BaseModel):
    """submissions_insertの束縛引数。SQLで使用する項目だけを受け付ける。"""

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


def submissions_insert(db: Database, params: SubmissionsInsertParams) -> int:
    "現在の組織の承認申請を、対象の文書版・申請者・審査状態・検証用ハッシュとともに登録する。"
    return db.execute(
        "operations/documents/submit_version/sql/005_submissions_insert.sql", params.model_dump()
    )


class VersionsInsertParams(BaseModel):
    """versions_insertの束縛引数。SQLで使用する項目だけを受け付ける。"""

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


def versions_insert(db: Database, params: VersionsInsertParams) -> int:
    "現在の組織の文書版を、版番号・本文の保存先・画像構成・検証用ハッシュを指定して登録する。"
    return db.execute(
        "operations/documents/submit_version/sql/006_versions_insert.sql", params.model_dump()
    )
