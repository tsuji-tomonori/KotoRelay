"""DDL・SQLから生成した型付き境界。直接編集しない。
SHA256: 53a0f16b07c496958b84965191a6388b846138e6a41f6ca6898895b8ad24a826
"""

from datetime import datetime

from pydantic import BaseModel, ConfigDict

from kotorelay.db import Database
from kotorelay.generated.models import (
    DepartmentsRow,
)


class DepartmentsListParams(BaseModel):
    """departments_listの束縛引数。SQLで使用する項目だけを受け付ける。"""

    model_config = ConfigDict(extra="forbid")
    organization_id: str


class DepartmentsListRow(DepartmentsRow):
    """departments_listのSELECT句に対応する取得行。"""

    model_config = ConfigDict(extra="forbid")
    id: str
    organization_id: str
    name: str
    active: bool


def departments_list(db: Database, params: DepartmentsListParams) -> list[DepartmentsListRow]:
    "現在の組織に属する部署を識別子順に一覧取得する。"
    return db.query(
        "operations/documents/change_policy/sql/001_departments_list.sql",
        params.model_dump(),
        DepartmentsListRow,
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
        "operations/documents/change_policy/sql/002_documents_update.sql", params.model_dump()
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
        "operations/documents/change_policy/sql/003_outbox_insert.sql", params.model_dump()
    )
