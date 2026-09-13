"""DDL・SQLから生成した型付き境界。直接編集しない。
SHA256: 1650f19b527e4849abfa37b86555576fe11e0589903be098cf22f76a46fbbcb2
"""

from datetime import datetime

from pydantic import BaseModel, ConfigDict

from kotorelay.db import Database
from kotorelay.generated.models import (
    AssetsRow,
)


class AssetsInsertParams(BaseModel):
    """assets_insertの束縛引数。SQLで使用する項目だけを受け付ける。"""

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


def assets_insert(db: Database, params: AssetsInsertParams) -> int:
    "現在の組織の文書に添付した画像の保存先・形式・寸法・検証用ハッシュを登録する。"
    return db.execute(
        "operations/images/upload_image/sql/001_assets_insert.sql", params.model_dump()
    )


class AssetsListParams(BaseModel):
    """assets_listの束縛引数。SQLで使用する項目だけを受け付ける。"""

    model_config = ConfigDict(extra="forbid")
    organization_id: str


class AssetsListRow(AssetsRow):
    """assets_listのSELECT句に対応する取得行。"""

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


def assets_list(db: Database, params: AssetsListParams) -> list[AssetsListRow]:
    "現在の組織に属する添付画像を識別子順に一覧取得する。"
    return db.query(
        "operations/images/upload_image/sql/002_assets_list.sql", params.model_dump(), AssetsListRow
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
        "operations/images/upload_image/sql/003_ocr_runs_insert.sql", params.model_dump()
    )
