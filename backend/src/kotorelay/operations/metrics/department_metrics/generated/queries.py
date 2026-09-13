"""DDL・SQLから生成した型付き境界。直接編集しない。
SHA256: 9c426268f25f745c3beb8cf0212c9fe8d349b7631837822235bcabbf74f79d28
"""

from kotorelay.db import Database
from kotorelay.generated.models import (
    DocumentsRow,
    EventsRow,
)


def documents_list(db: Database, organization_id: str) -> list[DocumentsRow]:
    "現在の組織に属する文書を識別子順に一覧取得する。"
    return db.query(
        "operations/metrics/department_metrics/sql/documents_list.sql",
        {"organization_id": organization_id},
        DocumentsRow,
    )


def events_list(db: Database, organization_id: str) -> list[EventsRow]:
    "現在の組織に属する利用イベントを識別子順に一覧取得する。"
    return db.query(
        "operations/metrics/department_metrics/sql/events_list.sql",
        {"organization_id": organization_id},
        EventsRow,
    )
