"""DDL・SQLから生成した型付き境界。直接編集しない。
SHA256: 8cdc42f5241337721cba6453c80f16a537254b677e7844973ad72096a381956d
"""

from kotorelay.db import Database
from kotorelay.generated.models import (
    DocumentsRow,
    OutboxRow,
    VersionsRow,
)


def documents_list(db: Database, organization_id: str) -> list[DocumentsRow]:
    "現在の組織に属する文書を識別子順に一覧取得する。"
    return db.query(
        "operations/indexing/list_jobs/sql/documents_list.sql",
        {"organization_id": organization_id},
        DocumentsRow,
    )


def outbox_list(db: Database, organization_id: str) -> list[OutboxRow]:
    "現在の組織に属する反映・削除ジョブを識別子順に一覧取得する。"
    return db.query(
        "operations/indexing/list_jobs/sql/outbox_list.sql",
        {"organization_id": organization_id},
        OutboxRow,
    )


def versions_list(db: Database, organization_id: str) -> list[VersionsRow]:
    "現在の組織に属する文書版を識別子順に一覧取得する。"
    return db.query(
        "operations/indexing/list_jobs/sql/versions_list.sql",
        {"organization_id": organization_id},
        VersionsRow,
    )
