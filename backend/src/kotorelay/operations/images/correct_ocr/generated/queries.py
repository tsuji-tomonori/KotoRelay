"""DDL・SQLから生成した型付き境界。直接編集しない。
SHA256: d09213799e980ae409bc873f7a946019a48f5c4382671332456fd1f981d98d49
"""

from kotorelay.db import Database
from kotorelay.generated.models import (
    AssetsRow,
    OcrRunsRow,
)


def assets_get(db: Database, organization_id: str, id: str) -> list[AssetsRow]:
    "現在の組織に属する指定の添付画像について、画像の保存先・形式・寸法・検証用ハッシュを取得する。"
    return db.query(
        "operations/images/correct_ocr/sql/assets_get.sql",
        {"organization_id": organization_id, "id": id},
        AssetsRow,
    )


def ocr_runs_insert(db: Database, row: OcrRunsRow) -> int:
    "現在の組織の画像に対する文字認識の実行記録を、認識結果の保存先・検証用ハッシュ・確認状態とともに登録する。"
    return db.execute("operations/images/correct_ocr/sql/ocr_runs_insert.sql", row.model_dump())
