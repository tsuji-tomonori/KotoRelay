"""DDL・SQLから生成した型付き境界。直接編集しない。
SHA256: b76e5f1b85cbcf06b7f9f826634c7ebdac06d0dc813585e752145ce8dc546a0e
"""

from pydantic import BaseModel, ConfigDict

from kotorelay.db import Database
from kotorelay.generated.models import (
    MembershipsRow,
    UsersRow,
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
        "operations/groups/list_members/sql/001_memberships_list.sql",
        params.model_dump(),
        MembershipsListRow,
    )


class UsersListParams(BaseModel):
    """users_listの束縛引数。SQLで使用する項目だけを受け付ける。"""

    model_config = ConfigDict(extra="forbid")
    organization_id: str


class UsersListRow(UsersRow):
    """users_listのSELECT句に対応する取得行。"""

    model_config = ConfigDict(extra="forbid")
    id: str
    organization_id: str
    subject: str
    display_name: str
    active: bool
    operator: bool


def users_list(db: Database, params: UsersListParams) -> list[UsersListRow]:
    "現在の組織に属する利用者を識別子順に一覧取得する。"
    return db.query(
        "operations/groups/list_members/sql/002_users_list.sql", params.model_dump(), UsersListRow
    )
