"""DDL・SQLから生成した型付き境界。直接編集しない。
SHA256: a75c1569af35300306ff6019b8df36d2198d62622cf876cdef090d83f78be55a
"""

from pydantic import BaseModel, ConfigDict

from kotorelay.db import Database
from kotorelay.generated.models import (
    DepartmentsRow,
    MembershipsRow,
    UsersRow,
)


class DepartmentsGetParams(BaseModel):
    """departments_getの束縛引数。SQLで使用する項目だけを受け付ける。"""

    model_config = ConfigDict(extra="forbid")
    organization_id: str
    id: str


class DepartmentsGetRow(DepartmentsRow):
    """departments_getのSELECT句に対応する取得行。"""

    model_config = ConfigDict(extra="forbid")
    id: str
    organization_id: str
    name: str
    active: bool


def departments_get(db: Database, params: DepartmentsGetParams) -> list[DepartmentsGetRow]:
    "現在の組織に属する指定の部署について、部署名と有効状態を取得する。"
    return db.query(
        "operations/groups/change_membership/sql/001_departments_get.sql",
        params.model_dump(),
        DepartmentsGetRow,
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
        "operations/groups/change_membership/sql/002_memberships_insert.sql", params.model_dump()
    )


class MembershipsListParams(BaseModel):
    """memberships_listの束縛引数。SQLで使用する項目だけを受け付ける。"""

    model_config = ConfigDict(extra="forbid")
    organization_id: str


class MembershipsListRow(MembershipsRow):
    """memberships_listのSELECT句に対応する取得行。"""

    model_config = ConfigDict(extra="forbid")
    id: str
    organization_id: str
    department_id: str
    user_id: str
    leader: bool
    can_author: bool
    can_review: bool
    active: bool


def memberships_list(db: Database, params: MembershipsListParams) -> list[MembershipsListRow]:
    "現在の組織に属する部署所属を識別子順に一覧取得する。"
    return db.query(
        "operations/groups/change_membership/sql/003_memberships_list.sql",
        params.model_dump(),
        MembershipsListRow,
    )


class MembershipsUpdateParams(BaseModel):
    """memberships_updateの束縛引数。SQLで使用する項目だけを受け付ける。"""

    model_config = ConfigDict(extra="forbid")
    department_id: str
    user_id: str
    leader: bool
    can_author: bool
    can_review: bool
    active: bool
    organization_id: str
    id: str


def memberships_update(db: Database, params: MembershipsUpdateParams) -> int:
    "現在の組織に属する指定の部署所属について、所属部署・利用者・執筆や審査の権限・有効状態を更新する。"
    return db.execute(
        "operations/groups/change_membership/sql/004_memberships_update.sql", params.model_dump()
    )


class UsersGetParams(BaseModel):
    """users_getの束縛引数。SQLで使用する項目だけを受け付ける。"""

    model_config = ConfigDict(extra="forbid")
    organization_id: str
    id: str


class UsersGetRow(UsersRow):
    """users_getのSELECT句に対応する取得行。"""

    model_config = ConfigDict(extra="forbid")
    id: str
    organization_id: str
    subject: str
    display_name: str
    active: bool
    operator: bool


def users_get(db: Database, params: UsersGetParams) -> list[UsersGetRow]:
    "現在の組織に属する指定の利用者について、認証主体・表示名・有効状態・運用権限を取得する。"
    return db.query(
        "operations/groups/change_membership/sql/005_users_get.sql",
        params.model_dump(),
        UsersGetRow,
    )
