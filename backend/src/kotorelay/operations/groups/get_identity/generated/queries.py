"""DDL・SQLから生成した型付き境界。直接編集しない。
SHA256: d6c862ff01eba93a5213e44f6faad7ef9141b104ca044f72e7d6e65a8f380f45
"""

from pydantic import BaseModel, ConfigDict

from kotorelay.db import Database
from kotorelay.generated.models import (
    DepartmentsRow,
)


class DepartmentsListParams(BaseModel):
    """departments_listの束縛引数。SQLで使用する項目だけを受け付ける。"""

    model_config = ConfigDict(extra="forbid")
    organization_id: str


class DepartmentsListRow(DepartmentsRow):
    """departments_listのSELECT句に対応する取得行。"""

    model_config = ConfigDict(extra="forbid")
    id: str
    organization_id: str
    name: str
    active: bool


def departments_list(db: Database, params: DepartmentsListParams) -> list[DepartmentsListRow]:
    "現在の組織に属する部署を識別子順に一覧取得する。"
    return db.query(
        "operations/groups/get_identity/sql/001_departments_list.sql",
        params.model_dump(),
        DepartmentsListRow,
    )
