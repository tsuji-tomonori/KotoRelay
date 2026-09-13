"""DDL・SQLから生成した型付き境界。直接編集しない。
SHA256: 5da376a5721388610f01161475df58af6beae7054f52d1bc12f8aa16ead33e04
"""

from kotorelay.db import Database
from kotorelay.generated.models import (
    SubmissionsRow,
    VersionsRow,
)


def submissions_list(db: Database, organization_id: str) -> list[SubmissionsRow]:
    "現在の組織に属する承認申請を識別子順に一覧取得する。"
    return db.query(
        "operations/documents/version_history/sql/submissions_list.sql",
        {"organization_id": organization_id},
        SubmissionsRow,
    )


def versions_list(db: Database, organization_id: str) -> list[VersionsRow]:
    "現在の組織に属する文書版を識別子順に一覧取得する。"
    return db.query(
        "operations/documents/version_history/sql/versions_list.sql",
        {"organization_id": organization_id},
        VersionsRow,
    )
