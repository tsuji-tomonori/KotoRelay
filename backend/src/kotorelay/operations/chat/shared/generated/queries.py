"""DDL・SQLから生成した型付き境界。直接編集しない。
SHA256: ad821ee2ce86c87a7ca3077a6a799e90db9ffeca3ac5e8b4e1cab5ea8862b7a2
"""

from datetime import datetime

from pydantic import BaseModel, ConfigDict

from kotorelay.db import Database
from kotorelay.generated.models import (
    AssetsRow,
    ChunksRow,
    DocumentsRow,
    OcrRunsRow,
    VersionsRow,
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
        "operations/chat/shared/sql/001_assets_get.sql", params.model_dump(), AssetsGetRow
    )


class ChunksGetParams(BaseModel):
    """chunks_getの束縛引数。SQLで使用する項目だけを受け付ける。"""

    model_config = ConfigDict(extra="forbid")
    organization_id: str
    id: str


class ChunksGetRow(ChunksRow):
    """chunks_getのSELECT句に対応する取得行。"""

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


def chunks_get(db: Database, params: ChunksGetParams) -> list[ChunksGetRow]:
    "現在の組織に属する指定の検索用の文書断片について、本文の保存先・出典の版・画像配置・索引反映状態を取得する。"
    return db.query(
        "operations/chat/shared/sql/002_chunks_get.sql", params.model_dump(), ChunksGetRow
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
        "operations/chat/shared/sql/003_documents_get.sql", params.model_dump(), DocumentsGetRow
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
        "operations/chat/shared/sql/004_ocr_runs_get.sql", params.model_dump(), OcrRunsGetRow
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
        "operations/chat/shared/sql/005_versions_get.sql", params.model_dump(), VersionsGetRow
    )
