"""DDL・SQLから生成した型付き境界。直接編集しない。
SHA256: a75c1569af35300306ff6019b8df36d2198d62622cf876cdef090d83f78be55a
"""

from kotorelay.db import Database
from kotorelay.generated.models import (
    DepartmentsRow,
    MembershipsRow,
    UsersRow,
)


def departments_get(db: Database, organization_id: str, id: str) -> list[DepartmentsRow]:
    "現在の組織に属する指定の部署について、部署名と有効状態を取得する。"
    return db.query(
        "operations/groups/change_membership/sql/departments_get.sql",
        {"organization_id": organization_id, "id": id},
        DepartmentsRow,
    )


def memberships_insert(db: Database, row: MembershipsRow) -> int:
    "現在の組織の利用者の部署所属を、所属部署・権限・有効状態を指定して登録する。"
    return db.execute(
        "operations/groups/change_membership/sql/memberships_insert.sql", row.model_dump()
    )


def memberships_list(db: Database, organization_id: str) -> list[MembershipsRow]:
    "現在の組織に属する部署所属を識別子順に一覧取得する。"
    return db.query(
        "operations/groups/change_membership/sql/memberships_list.sql",
        {"organization_id": organization_id},
        MembershipsRow,
    )


def memberships_update(db: Database, row: MembershipsRow) -> int:
    "現在の組織に属する指定の部署所属について、所属部署・利用者・執筆や審査の権限・有効状態を更新する。"
    return db.execute(
        "operations/groups/change_membership/sql/memberships_update.sql", row.model_dump()
    )


def users_get(db: Database, organization_id: str, id: str) -> list[UsersRow]:
    "現在の組織に属する指定の利用者について、認証主体・表示名・有効状態・運用権限を取得する。"
    return db.query(
        "operations/groups/change_membership/sql/users_get.sql",
        {"organization_id": organization_id, "id": id},
        UsersRow,
    )
