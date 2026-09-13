"""DDL・SQLから生成した型付き境界。直接編集しない。
SHA256: 9c426268f25f745c3beb8cf0212c9fe8d349b7631837822235bcabbf74f79d28
"""

from datetime import datetime

from pydantic import BaseModel, ConfigDict

from kotorelay.db import Database
from kotorelay.generated.models import (
    DocumentsRow,
    EventsRow,
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
        "operations/metrics/department_metrics/sql/001_documents_list.sql",
        params.model_dump(),
        DocumentsListRow,
    )


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
        "operations/metrics/department_metrics/sql/002_events_list.sql",
        params.model_dump(),
        EventsListRow,
    )
