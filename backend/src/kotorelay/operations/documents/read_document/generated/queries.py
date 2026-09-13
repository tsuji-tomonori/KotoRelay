"""DDL・SQLから生成した型付き境界。直接編集しない。
SHA256: 755a2db6805d6c83caa6a09b794a965b09ad82158fa0cc3db11e35634b16fe67
"""

from kotorelay.db import Database
from kotorelay.generated.models import ChunksRow, DocumentsRow


def chunks_list(db: Database, organization_id: str) -> list[ChunksRow]:
    "現在の組織に属する検索用の文書断片を識別子順に一覧取得する。"
    return db.query(
        "operations/documents/read_document/sql/chunks_list.sql",
        {"organization_id": organization_id},
        ChunksRow,
    )


def documents_get(db: Database, organization_id: str, id: str) -> list[DocumentsRow]:
    "現在の組織に属する指定の文書について、文書の所有部署・公開範囲・状態・公開版の参照を取得する。"
    return db.query(
        "operations/documents/read_document/sql/documents_get.sql",
        {"organization_id": organization_id, "id": id},
        DocumentsRow,
    )
