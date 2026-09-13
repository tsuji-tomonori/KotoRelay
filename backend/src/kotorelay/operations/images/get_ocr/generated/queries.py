"""DDL・SQLから生成した型付き境界。直接編集しない。
SHA256: e2c5e9668a6df900a812bf5eb2bbb517d33ebe20a024b332b212d4f35e183074
"""

from datetime import datetime

from pydantic import BaseModel, ConfigDict

from kotorelay.db import Database
from kotorelay.generated.models import (
    DocumentsRow,
    OcrRunsRow,
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
        "operations/images/get_ocr/sql/001_documents_get.sql", params.model_dump(), DocumentsGetRow
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
        "operations/images/get_ocr/sql/002_ocr_runs_get.sql", params.model_dump(), OcrRunsGetRow
    )
