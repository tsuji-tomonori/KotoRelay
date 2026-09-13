"""DDL・SQLから生成した型付き境界。直接編集しない。
SHA256: 53a0f16b07c496958b84965191a6388b846138e6a41f6ca6898895b8ad24a826
"""

from kotorelay.db import Database
from kotorelay.generated.models import (
    DepartmentsRow,
    DocumentsRow,
    OutboxRow,
)


def departments_list(db: Database, organization_id: str) -> list[DepartmentsRow]:
    "現在の組織に属する部署を識別子順に一覧取得する。"
    return db.query(
        "operations/documents/change_policy/sql/departments_list.sql",
        {"organization_id": organization_id},
        DepartmentsRow,
    )


def documents_update(db: Database, row: DocumentsRow) -> int:
    "現在の組織に属する指定の文書について、文書の所有部署・公開範囲・状態・公開版の参照を更新する。"
    return db.execute(
        "operations/documents/change_policy/sql/documents_update.sql", row.model_dump()
    )


def outbox_insert(db: Database, row: OutboxRow) -> int:
    "現在の組織の反映・削除ジョブを、対象文書と版・処理種別を指定して登録する。"
    return db.execute("operations/documents/change_policy/sql/outbox_insert.sql", row.model_dump())
