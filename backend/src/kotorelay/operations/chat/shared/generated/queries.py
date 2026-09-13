"""DDL・SQLから生成した型付き境界。直接編集しない。
SHA256: ad821ee2ce86c87a7ca3077a6a799e90db9ffeca3ac5e8b4e1cab5ea8862b7a2
"""

from kotorelay.db import Database
from kotorelay.generated.models import (
    AssetsRow,
    ChunksRow,
    DocumentsRow,
    OcrRunsRow,
    VersionsRow,
)


def assets_get(db: Database, organization_id: str, id: str) -> list[AssetsRow]:
    "現在の組織に属する指定の添付画像について、画像の保存先・形式・寸法・検証用ハッシュを取得する。"
    return db.query(
        "operations/chat/shared/sql/assets_get.sql",
        {"organization_id": organization_id, "id": id},
        AssetsRow,
    )


def chunks_get(db: Database, organization_id: str, id: str) -> list[ChunksRow]:
    "現在の組織に属する指定の検索用の文書断片について、本文の保存先・出典の版・画像配置・索引反映状態を取得する。"
    return db.query(
        "operations/chat/shared/sql/chunks_get.sql",
        {"organization_id": organization_id, "id": id},
        ChunksRow,
    )


def documents_get(db: Database, organization_id: str, id: str) -> list[DocumentsRow]:
    "現在の組織に属する指定の文書について、文書の所有部署・公開範囲・状態・公開版の参照を取得する。"
    return db.query(
        "operations/chat/shared/sql/documents_get.sql",
        {"organization_id": organization_id, "id": id},
        DocumentsRow,
    )


def ocr_runs_get(db: Database, organization_id: str, id: str) -> list[OcrRunsRow]:
    "現在の組織に属する指定の文字認識の実行記録について、認識結果の保存先・検証用ハッシュ・確認状態を取得する。"
    return db.query(
        "operations/chat/shared/sql/ocr_runs_get.sql",
        {"organization_id": organization_id, "id": id},
        OcrRunsRow,
    )


def versions_get(db: Database, organization_id: str, id: str) -> list[VersionsRow]:
    "現在の組織に属する指定の文書版について、確定した本文の保存先と画像構成・検証用ハッシュを取得する。"
    return db.query(
        "operations/chat/shared/sql/versions_get.sql",
        {"organization_id": organization_id, "id": id},
        VersionsRow,
    )
