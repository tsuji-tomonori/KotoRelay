"""DDL・SQLから生成した型付き境界。直接編集しない。
SHA256: 7e39b557835d0756a7dbd5ccc793d2378fa557913daf20185611845ed608baaa
"""

from kotorelay.db import Database
from kotorelay.generated.models import (
    AssetsRow,
    DocumentsRow,
    DraftsRow,
    OcrRunsRow,
    SubmissionsRow,
    VersionsRow,
)


def assets_get(db: Database, organization_id: str, id: str) -> list[AssetsRow]:
    "現在の組織に属する指定の添付画像について、画像の保存先・形式・寸法・検証用ハッシュを取得する。"
    return db.query(
        "operations/documents/submit_version/sql/assets_get.sql",
        {"organization_id": organization_id, "id": id},
        AssetsRow,
    )


def documents_update(db: Database, row: DocumentsRow) -> int:
    "現在の組織に属する指定の文書について、文書の所有部署・公開範囲・状態・公開版の参照を更新する。"
    return db.execute(
        "operations/documents/submit_version/sql/documents_update.sql", row.model_dump()
    )


def drafts_list(db: Database, organization_id: str) -> list[DraftsRow]:
    "現在の組織に属する下書きを識別子順に一覧取得する。"
    return db.query(
        "operations/documents/submit_version/sql/drafts_list.sql",
        {"organization_id": organization_id},
        DraftsRow,
    )


def ocr_runs_get(db: Database, organization_id: str, id: str) -> list[OcrRunsRow]:
    "現在の組織に属する指定の文字認識の実行記録について、認識結果の保存先・検証用ハッシュ・確認状態を取得する。"
    return db.query(
        "operations/documents/submit_version/sql/ocr_runs_get.sql",
        {"organization_id": organization_id, "id": id},
        OcrRunsRow,
    )


def submissions_insert(db: Database, row: SubmissionsRow) -> int:
    "現在の組織の承認申請を、対象の文書版・申請者・審査状態・検証用ハッシュとともに登録する。"
    return db.execute(
        "operations/documents/submit_version/sql/submissions_insert.sql", row.model_dump()
    )


def versions_insert(db: Database, row: VersionsRow) -> int:
    "現在の組織の文書版を、版番号・本文の保存先・画像構成・検証用ハッシュを指定して登録する。"
    return db.execute(
        "operations/documents/submit_version/sql/versions_insert.sql", row.model_dump()
    )
