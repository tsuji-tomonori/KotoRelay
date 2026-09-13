"""DDL・SQLから生成した型付き境界。直接編集しない。
SHA256: 62be91fe6530dfd850f1ec870d4b3a62483674baf1b41fba5e41708980f7a76e
"""

from kotorelay.db import Database
from kotorelay.generated.models import (
    DocumentsRow,
    OutboxRow,
    SubmissionsRow,
    VersionsRow,
)


def documents_update(db: Database, row: DocumentsRow) -> int:
    "現在の組織に属する指定の文書について、文書の所有部署・公開範囲・状態・公開版の参照を更新する。"
    return db.execute("operations/reviews/decide_review/sql/documents_update.sql", row.model_dump())


def outbox_insert(db: Database, row: OutboxRow) -> int:
    "現在の組織の反映・削除ジョブを、対象文書と版・処理種別を指定して登録する。"
    return db.execute("operations/reviews/decide_review/sql/outbox_insert.sql", row.model_dump())


def submissions_get(db: Database, organization_id: str, id: str) -> list[SubmissionsRow]:
    "現在の組織に属する指定の承認申請について、対象の文書版・審査状態・判断者・理由を取得する。"
    return db.query(
        "operations/reviews/decide_review/sql/submissions_get.sql",
        {"organization_id": organization_id, "id": id},
        SubmissionsRow,
    )


def submissions_update(db: Database, row: SubmissionsRow) -> int:
    "現在の組織に属する指定の承認申請について、対象の文書版・審査状態・判断者・理由を更新する。"
    return db.execute(
        "operations/reviews/decide_review/sql/submissions_update.sql", row.model_dump()
    )


def versions_get(db: Database, organization_id: str, id: str) -> list[VersionsRow]:
    "現在の組織に属する指定の文書版について、確定した本文の保存先と画像構成・検証用ハッシュを取得する。"
    return db.query(
        "operations/reviews/decide_review/sql/versions_get.sql",
        {"organization_id": organization_id, "id": id},
        VersionsRow,
    )
