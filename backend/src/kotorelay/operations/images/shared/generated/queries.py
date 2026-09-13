"""DDL・SQLから生成した型付き境界。直接編集しない。
SHA256: 1504f79d9731e45de6d311cbf5b0554cacfbc95617b769cd8909eb3e737010e3
"""

from kotorelay.db import Database
from kotorelay.generated.models import (
    AssetsRow,
    DocumentsRow,
)


def assets_get(db: Database, organization_id: str, id: str) -> list[AssetsRow]:
    "現在の組織に属する指定の添付画像について、画像の保存先・形式・寸法・検証用ハッシュを取得する。"
    return db.query(
        "operations/images/shared/sql/assets_get.sql",
        {"organization_id": organization_id, "id": id},
        AssetsRow,
    )


def documents_get(db: Database, organization_id: str, id: str) -> list[DocumentsRow]:
    "現在の組織に属する指定の文書について、文書の所有部署・公開範囲・状態・公開版の参照を取得する。"
    return db.query(
        "operations/images/shared/sql/documents_get.sql",
        {"organization_id": organization_id, "id": id},
        DocumentsRow,
    )
