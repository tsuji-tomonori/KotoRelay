"""DDL・SQLから生成した型付き境界。直接編集しない。
SHA256: a138ea6cb8eecaa6d4c973c16d74b554224d5cce1ee6a7d293a789a3b5d692eb
"""

from pydantic import BaseModel, ConfigDict

from kotorelay.db import Database
from kotorelay.generated.models import (
    OrganizationsRow,
)


class DepartmentsInsertParams(BaseModel):
    """departments_insertの束縛引数。SQLで使用する項目だけを受け付ける。"""

    model_config = ConfigDict(extra="forbid")
    id: str
    organization_id: str
    name: str
    active: bool


def departments_insert(db: Database, params: DepartmentsInsertParams) -> int:
    "現在の組織の部署を、部署名と有効状態を指定して登録する。"
    return db.execute(
        "operations/system/bootstrap/sql/001_departments_insert.sql", params.model_dump()
    )


class MembershipsInsertParams(BaseModel):
    """memberships_insertの束縛引数。SQLで使用する項目だけを受け付ける。"""

    model_config = ConfigDict(extra="forbid")
    id: str
    organization_id: str
    department_id: str
    user_id: str
    leader: bool
    can_author: bool
    can_review: bool
    active: bool


def memberships_insert(db: Database, params: MembershipsInsertParams) -> int:
    "現在の組織の利用者の部署所属を、所属部署・権限・有効状態を指定して登録する。"
    return db.execute(
        "operations/system/bootstrap/sql/002_memberships_insert.sql", params.model_dump()
    )


class OrganizationsGetParams(BaseModel):
    """organizations_getの束縛引数。SQLで使用する項目だけを受け付ける。"""

    model_config = ConfigDict(extra="forbid")
    organization_id: str
    id: str


class OrganizationsGetRow(OrganizationsRow):
    """organizations_getのSELECT句に対応する取得行。"""

    model_config = ConfigDict(extra="forbid")
    id: str
    organization_id: str
    name: str
    revision: int
    suspended: bool


def organizations_get(db: Database, params: OrganizationsGetParams) -> list[OrganizationsGetRow]:
    "現在の組織の組織名・改訂番号・利用停止状態を取得する。"
    return db.query(
        "operations/system/bootstrap/sql/003_organizations_get.sql",
        params.model_dump(),
        OrganizationsGetRow,
    )


class OrganizationsInsertParams(BaseModel):
    """organizations_insertの束縛引数。SQLで使用する項目だけを受け付ける。"""

    model_config = ConfigDict(extra="forbid")
    id: str
    organization_id: str
    name: str
    revision: int
    suspended: bool


def organizations_insert(db: Database, params: OrganizationsInsertParams) -> int:
    "組織を、組織名・改訂番号・利用停止状態を指定して登録する。"
    return db.execute(
        "operations/system/bootstrap/sql/004_organizations_insert.sql", params.model_dump()
    )


class UsersInsertParams(BaseModel):
    """users_insertの束縛引数。SQLで使用する項目だけを受け付ける。"""

    model_config = ConfigDict(extra="forbid")
    id: str
    organization_id: str
    subject: str
    display_name: str
    active: bool
    operator: bool


def users_insert(db: Database, params: UsersInsertParams) -> int:
    "現在の組織の利用者を、認証主体・表示名・有効状態・運用権限を指定して登録する。"
    return db.execute("operations/system/bootstrap/sql/005_users_insert.sql", params.model_dump())
