"""DDL・SQLから生成した型付き境界。直接編集しない。
SHA256: 2d693a1d802faace7d96ef3f1310723a2187a0f3024d85125ef4fd441c0d6443
"""

from kotorelay.db import Database
from kotorelay.generated.models import (
    DocumentsRow,
    DraftsRow,
)


def documents_insert(db: Database, row: DocumentsRow) -> int:
    "現在の組織の文書を、所有部署・公開範囲・状態を指定して登録する。"
    return db.execute(
        "operations/documents/create_document/sql/documents_insert.sql", row.model_dump()
    )


def drafts_insert(db: Database, row: DraftsRow) -> int:
    "現在の組織の文書の下書きを、本文の保存先・画像配置・改訂番号を指定して登録する。"
    return db.execute(
        "operations/documents/create_document/sql/drafts_insert.sql", row.model_dump()
    )
