"""change_membershipの入力制約と応答型を定義する。"""

from __future__ import annotations

from kotorelay.generated import models
from kotorelay.schemas import Id, Input


class ChangeMembership(Input):
    user_id: Id
    department_id: Id
    leader: bool = False
    can_author: bool = False
    can_review: bool = False
    active: bool = True


type ResponseData = models.MembershipsRow
