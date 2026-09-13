"""DDL・SQLから生成した型付き境界。直接編集しない。
SHA256: 62be91fe6530dfd850f1ec870d4b3a62483674baf1b41fba5e41708980f7a76e
"""

from datetime import datetime

from pydantic import BaseModel, ConfigDict

from kotorelay.db import Database
from kotorelay.generated.models import (
    SubmissionsRow,
    VersionsRow,
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
        "operations/reviews/decide_review/sql/001_documents_update.sql", params.model_dump()
    )


class OutboxInsertParams(BaseModel):
    """outbox_insertの束縛引数。SQLで使用する項目だけを受け付ける。"""

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


def outbox_insert(db: Database, params: OutboxInsertParams) -> int:
    "現在の組織の反映・削除ジョブを、対象文書と版・処理種別を指定して登録する。"
    return db.execute(
        "operations/reviews/decide_review/sql/002_outbox_insert.sql", params.model_dump()
    )


class SubmissionsGetParams(BaseModel):
    """submissions_getの束縛引数。SQLで使用する項目だけを受け付ける。"""

    model_config = ConfigDict(extra="forbid")
    organization_id: str
    id: str


class SubmissionsGetRow(SubmissionsRow):
    """submissions_getのSELECT句に対応する取得行。"""

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


def submissions_get(db: Database, params: SubmissionsGetParams) -> list[SubmissionsGetRow]:
    "現在の組織に属する指定の承認申請について、対象の文書版・審査状態・判断者・理由を取得する。"
    return db.query(
        "operations/reviews/decide_review/sql/003_submissions_get.sql",
        params.model_dump(),
        SubmissionsGetRow,
    )


class SubmissionsUpdateParams(BaseModel):
    """submissions_updateの束縛引数。SQLで使用する項目だけを受け付ける。"""

    model_config = ConfigDict(extra="forbid")
    document_id: str
    version_id: str
    requested_by: str
    status: str
    manifest_hash: str
    decided_by: str | None
    reason: str
    created_at: datetime
    decided_at: datetime | None
    organization_id: str
    id: str


def submissions_update(db: Database, params: SubmissionsUpdateParams) -> int:
    "現在の組織に属する指定の承認申請について、対象の文書版・審査状態・判断者・理由を更新する。"
    return db.execute(
        "operations/reviews/decide_review/sql/004_submissions_update.sql", params.model_dump()
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
        "operations/reviews/decide_review/sql/005_versions_get.sql",
        params.model_dump(),
        VersionsGetRow,
    )
