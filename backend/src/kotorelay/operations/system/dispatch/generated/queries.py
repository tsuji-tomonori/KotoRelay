"""DDL・SQLから生成した型付き境界。直接編集しない。
SHA256: cce97c744d57b159d52bf57473ef3cb8be296952f1742a2c4fc9f8c6f33e6d6c
"""

from kotorelay.db import Database
from kotorelay.generated.models import OutboxRow


def outbox_list(db: Database, organization_id: str) -> list[OutboxRow]:
    "現在の組織に属する反映・削除ジョブを識別子順に一覧取得する。"
    return db.query(
        "operations/system/dispatch/sql/outbox_list.sql",
        {"organization_id": organization_id},
        OutboxRow,
    )
