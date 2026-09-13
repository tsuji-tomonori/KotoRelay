"""DDL・SQLから生成した型付き境界。直接編集しない。
SHA256: 1504f79d9731e45de6d311cbf5b0554cacfbc95617b769cd8909eb3e737010e3
"""

from datetime import datetime

from pydantic import BaseModel, ConfigDict

from kotorelay.db import Database
from kotorelay.generated.models import (
    AssetsRow,
    DocumentsRow,
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
        "operations/images/shared/sql/001_assets_get.sql", params.model_dump(), AssetsGetRow
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
        "operations/images/shared/sql/002_documents_get.sql", params.model_dump(), DocumentsGetRow
    )
