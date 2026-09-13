"""DDL・SQLから生成した型付き境界。直接編集しない。
SHA256: 1650f19b527e4849abfa37b86555576fe11e0589903be098cf22f76a46fbbcb2
"""

from kotorelay.db import Database
from kotorelay.generated.models import (
    AssetsRow,
    OcrRunsRow,
)


def assets_insert(db: Database, row: AssetsRow) -> int:
    "現在の組織の文書に添付した画像の保存先・形式・寸法・検証用ハッシュを登録する。"
    return db.execute("operations/images/upload_image/sql/assets_insert.sql", row.model_dump())


def assets_list(db: Database, organization_id: str) -> list[AssetsRow]:
    "現在の組織に属する添付画像を識別子順に一覧取得する。"
    return db.query(
        "operations/images/upload_image/sql/assets_list.sql",
        {"organization_id": organization_id},
        AssetsRow,
    )


def ocr_runs_insert(db: Database, row: OcrRunsRow) -> int:
    "現在の組織の画像に対する文字認識の実行記録を、認識結果の保存先・検証用ハッシュ・確認状態とともに登録する。"
    return db.execute("operations/images/upload_image/sql/ocr_runs_insert.sql", row.model_dump())
