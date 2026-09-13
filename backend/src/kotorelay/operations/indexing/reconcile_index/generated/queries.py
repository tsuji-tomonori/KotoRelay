"""DDL・SQLから生成した型付き境界。直接編集しない。
SHA256: 17ac3cbec7d2ce1494f104b2d942d456201c53d974ff44607341d3b162b94cc1
"""

from kotorelay.db import Database
from kotorelay.generated.models import ChunksRow, DocumentsRow


def chunks_list(db: Database, organization_id: str) -> list[ChunksRow]:
    "現在の組織に属する検索用の文書断片を識別子順に一覧取得する。"
    return db.query(
        "operations/indexing/reconcile_index/sql/chunks_list.sql",
        {"organization_id": organization_id},
        ChunksRow,
    )


def documents_list(db: Database, organization_id: str) -> list[DocumentsRow]:
    "現在の組織に属する文書を識別子順に一覧取得する。"
    return db.query(
        "operations/indexing/reconcile_index/sql/documents_list.sql",
        {"organization_id": organization_id},
        DocumentsRow,
    )
