"""DDL・SQLから生成した型付き境界。直接編集しない。
SHA256: a138ea6cb8eecaa6d4c973c16d74b554224d5cce1ee6a7d293a789a3b5d692eb
"""

from kotorelay.db import Database
from kotorelay.generated.models import (
    DepartmentsRow,
    MembershipsRow,
    OrganizationsRow,
    UsersRow,
)


def departments_insert(db: Database, row: DepartmentsRow) -> int:
    "現在の組織の部署を、部署名と有効状態を指定して登録する。"
    return db.execute("operations/system/bootstrap/sql/departments_insert.sql", row.model_dump())


def memberships_insert(db: Database, row: MembershipsRow) -> int:
    "現在の組織の利用者の部署所属を、所属部署・権限・有効状態を指定して登録する。"
    return db.execute("operations/system/bootstrap/sql/memberships_insert.sql", row.model_dump())


def organizations_get(db: Database, organization_id: str, id: str) -> list[OrganizationsRow]:
    "現在の組織の組織名・改訂番号・利用停止状態を取得する。"
    return db.query(
        "operations/system/bootstrap/sql/organizations_get.sql",
        {"organization_id": organization_id, "id": id},
        OrganizationsRow,
    )


def organizations_insert(db: Database, row: OrganizationsRow) -> int:
    "組織を、組織名・改訂番号・利用停止状態を指定して登録する。"
    return db.execute("operations/system/bootstrap/sql/organizations_insert.sql", row.model_dump())


def users_insert(db: Database, row: UsersRow) -> int:
    "現在の組織の利用者を、認証主体・表示名・有効状態・運用権限を指定して登録する。"
    return db.execute("operations/system/bootstrap/sql/users_insert.sql", row.model_dump())
