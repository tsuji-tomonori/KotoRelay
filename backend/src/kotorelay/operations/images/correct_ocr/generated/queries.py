"""DDL・SQLから生成した型付き境界。直接編集しない。
SHA256: d09213799e980ae409bc873f7a946019a48f5c4382671332456fd1f981d98d49
"""

from datetime import datetime

from pydantic import BaseModel, ConfigDict

from kotorelay.db import Database
from kotorelay.generated.models import (
    AssetsRow,
)


class AssetsGetParams(BaseModel):
    """assets_getの束縛引数。SQLで使用する項目だけを受け付ける。"""

    model_config = ConfigDict(extra="forbid")
    organization_id: str
    id: str


class AssetsGetRow(AssetsRow):
    """assets_getのSELECT句に対応する取得行。"""

    model_config = ConfigDict(extra="forbid")
    id: str
    organization_id: str
    document_id: str
    object_key: str
    sha256: str
    media_type: str
    width: int
    height: int
    size: int
    created_at: datetime


def assets_get(db: Database, params: AssetsGetParams) -> list[AssetsGetRow]:
    "現在の組織に属する指定の添付画像について、画像の保存先・形式・寸法・検証用ハッシュを取得する。"
    return db.query(
        "operations/images/correct_ocr/sql/001_assets_get.sql", params.model_dump(), AssetsGetRow
    )


class OcrRunsInsertParams(BaseModel):
    """ocr_runs_insertの束縛引数。SQLで使用する項目だけを受け付ける。"""

    model_config = ConfigDict(extra="forbid")
    id: str
    organization_id: str
    document_id: str
    asset_id: str
    result_key: str
    result_hash: str
    engine: str
    status: str
    confirmed: bool
    created_at: datetime


def ocr_runs_insert(db: Database, params: OcrRunsInsertParams) -> int:
    "現在の組織の画像に対する文字認識の実行記録を、認識結果の保存先・検証用ハッシュ・確認状態とともに登録する。"
    return db.execute(
        "operations/images/correct_ocr/sql/002_ocr_runs_insert.sql", params.model_dump()
    )
