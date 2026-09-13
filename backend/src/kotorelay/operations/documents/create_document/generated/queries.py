"""DDL・SQLから生成した型付き境界。直接編集しない。
SHA256: 2d693a1d802faace7d96ef3f1310723a2187a0f3024d85125ef4fd441c0d6443
"""

from datetime import datetime

from pydantic import BaseModel, ConfigDict

from kotorelay.db import Database


class DocumentsInsertParams(BaseModel):
    """documents_insertの束縛引数。SQLで使用する項目だけを受け付ける。"""

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


def documents_insert(db: Database, params: DocumentsInsertParams) -> int:
    "現在の組織の文書を、所有部署・公開範囲・状態を指定して登録する。"
    return db.execute(
        "operations/documents/create_document/sql/001_documents_insert.sql", params.model_dump()
    )


class DraftsInsertParams(BaseModel):
    """drafts_insertの束縛引数。SQLで使用する項目だけを受け付ける。"""

    model_config = ConfigDict(extra="forbid")
    id: str
    organization_id: str
    document_id: str
    body_key: str
    body_hash: str
    placements: str
    revision: int
    updated_by: str


def drafts_insert(db: Database, params: DraftsInsertParams) -> int:
    "現在の組織の文書の下書きを、本文の保存先・画像配置・改訂番号を指定して登録する。"
    return db.execute(
        "operations/documents/create_document/sql/002_drafts_insert.sql", params.model_dump()
    )
