"""DDL・SQLから生成した型付き境界。直接編集しない。
SHA256: 5ca7f294a416ad5f399219768357be8e801485c13cf75605924dabd01a26db2d
"""

from kotorelay.db import Database
from kotorelay.generated.models import (
    AssetsRow,
    DocumentsRow,
    DraftsRow,
    OcrRunsRow,
)


def assets_get(db: Database, organization_id: str, id: str) -> list[AssetsRow]:
    "現在の組織に属する指定の添付画像について、画像の保存先・形式・寸法・検証用ハッシュを取得する。"
    return db.query(
        "operations/documents/save_draft/sql/assets_get.sql",
        {"organization_id": organization_id, "id": id},
        AssetsRow,
    )


def documents_update(db: Database, row: DocumentsRow) -> int:
    "現在の組織に属する指定の文書について、文書の所有部署・公開範囲・状態・公開版の参照を更新する。"
    return db.execute("operations/documents/save_draft/sql/documents_update.sql", row.model_dump())


def drafts_list(db: Database, organization_id: str) -> list[DraftsRow]:
    "現在の組織に属する下書きを識別子順に一覧取得する。"
    return db.query(
        "operations/documents/save_draft/sql/drafts_list.sql",
        {"organization_id": organization_id},
        DraftsRow,
    )


def drafts_update(db: Database, row: DraftsRow) -> int:
    "現在の組織に属する指定の下書きについて、本文の保存先・画像配置・改訂番号を更新する。"
    return db.execute("operations/documents/save_draft/sql/drafts_update.sql", row.model_dump())


def ocr_runs_get(db: Database, organization_id: str, id: str) -> list[OcrRunsRow]:
    "現在の組織に属する指定の文字認識の実行記録について、認識結果の保存先・検証用ハッシュ・確認状態を取得する。"
    return db.query(
        "operations/documents/save_draft/sql/ocr_runs_get.sql",
        {"organization_id": organization_id, "id": id},
        OcrRunsRow,
    )
