"""DDL・SQLから生成した型付き境界。直接編集しない。
SHA256: 755a2db6805d6c83caa6a09b794a965b09ad82158fa0cc3db11e35634b16fe67
"""

from datetime import datetime

from pydantic import BaseModel, ConfigDict

from kotorelay.db import Database
from kotorelay.generated.models import (
    ChunksRow,
    DocumentsRow,
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
        "operations/documents/read_document/sql/001_chunks_list.sql",
        params.model_dump(),
        ChunksListRow,
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
        "operations/documents/read_document/sql/002_documents_get.sql",
        params.model_dump(),
        DocumentsGetRow,
    )
