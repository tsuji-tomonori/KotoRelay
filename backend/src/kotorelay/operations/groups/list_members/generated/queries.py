"""DDL・SQLから生成した型付き境界。直接編集しない。
SHA256: b76e5f1b85cbcf06b7f9f826634c7ebdac06d0dc813585e752145ce8dc546a0e
"""

from kotorelay.db import Database
from kotorelay.generated.models import (
    MembershipsRow,
    UsersRow,
)


def memberships_list(db: Database, organization_id: str) -> list[MembershipsRow]:
    "現在の組織に属する部署所属を識別子順に一覧取得する。"
    return db.query(
        "operations/groups/list_members/sql/memberships_list.sql",
        {"organization_id": organization_id},
        MembershipsRow,
    )


def users_list(db: Database, organization_id: str) -> list[UsersRow]:
    "現在の組織に属する利用者を識別子順に一覧取得する。"
    return db.query(
        "operations/groups/list_members/sql/users_list.sql",
        {"organization_id": organization_id},
        UsersRow,
    )
