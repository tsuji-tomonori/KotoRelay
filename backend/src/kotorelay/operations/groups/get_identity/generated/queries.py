"""DDL・SQLから生成した型付き境界。直接編集しない。
SHA256: d6c862ff01eba93a5213e44f6faad7ef9141b104ca044f72e7d6e65a8f380f45
"""

from kotorelay.db import Database
from kotorelay.generated.models import DepartmentsRow


def departments_list(db: Database, organization_id: str) -> list[DepartmentsRow]:
    "現在の組織に属する部署を識別子順に一覧取得する。"
    return db.query(
        "operations/groups/get_identity/sql/departments_list.sql",
        {"organization_id": organization_id},
        DepartmentsRow,
    )
