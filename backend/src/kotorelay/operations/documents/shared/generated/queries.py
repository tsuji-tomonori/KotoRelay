"""DDL・SQLから生成した型付き境界。直接編集しない。
SHA256: 4677d1201bf137cf7b6ffd7f3e38a53a11af6b303681a7110df446f144650f8e
"""

from kotorelay.db import Database
from kotorelay.generated.models import DraftsRow


def drafts_list(db: Database, organization_id: str) -> list[DraftsRow]:
    "現在の組織に属する下書きを識別子順に一覧取得する。"
    return db.query(
        "operations/documents/shared/sql/drafts_list.sql",
        {"organization_id": organization_id},
        DraftsRow,
    )
