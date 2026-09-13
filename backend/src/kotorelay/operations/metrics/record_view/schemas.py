"""record_viewの入力制約と応答型を定義する。"""

from __future__ import annotations

from kotorelay.schemas import Id, Input


class ViewEvent(Input):
    id: Id
    department_id: Id


type ResponseData = dict[str, bool]
