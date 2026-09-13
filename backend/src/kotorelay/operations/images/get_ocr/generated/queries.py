"""DDL・SQLから生成した型付き境界。直接編集しない。
SHA256: e2c5e9668a6df900a812bf5eb2bbb517d33ebe20a024b332b212d4f35e183074
"""

from kotorelay.db import Database
from kotorelay.generated.models import (
    DocumentsRow,
    OcrRunsRow,
)


def documents_get(db: Database, organization_id: str, id: str) -> list[DocumentsRow]:
    "現在の組織に属する指定の文書について、文書の所有部署・公開範囲・状態・公開版の参照を取得する。"
    return db.query(
        "operations/images/get_ocr/sql/documents_get.sql",
        {"organization_id": organization_id, "id": id},
        DocumentsRow,
    )


def ocr_runs_get(db: Database, organization_id: str, id: str) -> list[OcrRunsRow]:
    "現在の組織に属する指定の文字認識の実行記録について、認識結果の保存先・検証用ハッシュ・確認状態を取得する。"
    return db.query(
        "operations/images/get_ocr/sql/ocr_runs_get.sql",
        {"organization_id": organization_id, "id": id},
        OcrRunsRow,
    )
