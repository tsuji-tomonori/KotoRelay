"""DDL・SQLから生成した型付き境界。直接編集しない。
SHA256: 50dbba107dd6935d5879f05f19e78ce01fe4d6aec3191780cc061e24fa250f14
"""

from kotorelay.db import Database
from kotorelay.generated.models import (
    AnswersRow,
    AssetsRow,
    ChunksRow,
    DocumentsRow,
    DraftsRow,
    OcrRunsRow,
    OutboxRow,
    VersionsRow,
)


def answers_list(db: Database, organization_id: str) -> list[AnswersRow]:
    "現在の組織に属する回答履歴を識別子順に一覧取得する。"
    return db.query(
        "operations/indexing/shared/sql/answers_list.sql",
        {"organization_id": organization_id},
        AnswersRow,
    )


def assets_delete(db: Database, organization_id: str, id: str) -> int:
    "現在の組織に属する指定の添付画像の記録を削除する。"
    return db.execute(
        "operations/indexing/shared/sql/assets_delete.sql",
        {"organization_id": organization_id, "id": id},
    )


def assets_get(db: Database, organization_id: str, id: str) -> list[AssetsRow]:
    "現在の組織に属する指定の添付画像について、画像の保存先・形式・寸法・検証用ハッシュを取得する。"
    return db.query(
        "operations/indexing/shared/sql/assets_get.sql",
        {"organization_id": organization_id, "id": id},
        AssetsRow,
    )


def assets_list(db: Database, organization_id: str) -> list[AssetsRow]:
    "現在の組織に属する添付画像を識別子順に一覧取得する。"
    return db.query(
        "operations/indexing/shared/sql/assets_list.sql",
        {"organization_id": organization_id},
        AssetsRow,
    )


def chunks_delete(db: Database, organization_id: str, id: str) -> int:
    "現在の組織に属する指定の検索用の文書断片の記録を削除する。"
    return db.execute(
        "operations/indexing/shared/sql/chunks_delete.sql",
        {"organization_id": organization_id, "id": id},
    )


def chunks_insert(db: Database, row: ChunksRow) -> int:
    "現在の組織の検索用の文書断片を、出典の版・本文の保存先・画像配置とともに登録する。"
    return db.execute("operations/indexing/shared/sql/chunks_insert.sql", row.model_dump())


def chunks_list(db: Database, organization_id: str) -> list[ChunksRow]:
    "現在の組織に属する検索用の文書断片を識別子順に一覧取得する。"
    return db.query(
        "operations/indexing/shared/sql/chunks_list.sql",
        {"organization_id": organization_id},
        ChunksRow,
    )


def chunks_update(db: Database, row: ChunksRow) -> int:
    "現在の組織に属する指定の検索用の文書断片について、本文の保存先・出典の版・画像配置・索引反映状態を更新する。"
    return db.execute("operations/indexing/shared/sql/chunks_update.sql", row.model_dump())


def documents_get(db: Database, organization_id: str, id: str) -> list[DocumentsRow]:
    "現在の組織に属する指定の文書について、文書の所有部署・公開範囲・状態・公開版の参照を取得する。"
    return db.query(
        "operations/indexing/shared/sql/documents_get.sql",
        {"organization_id": organization_id, "id": id},
        DocumentsRow,
    )


def documents_list(db: Database, organization_id: str) -> list[DocumentsRow]:
    "現在の組織に属する文書を識別子順に一覧取得する。"
    return db.query(
        "operations/indexing/shared/sql/documents_list.sql",
        {"organization_id": organization_id},
        DocumentsRow,
    )


def drafts_delete(db: Database, organization_id: str, id: str) -> int:
    "現在の組織に属する指定の下書きの記録を削除する。"
    return db.execute(
        "operations/indexing/shared/sql/drafts_delete.sql",
        {"organization_id": organization_id, "id": id},
    )


def drafts_list(db: Database, organization_id: str) -> list[DraftsRow]:
    "現在の組織に属する下書きを識別子順に一覧取得する。"
    return db.query(
        "operations/indexing/shared/sql/drafts_list.sql",
        {"organization_id": organization_id},
        DraftsRow,
    )


def ocr_runs_delete(db: Database, organization_id: str, id: str) -> int:
    "現在の組織に属する指定の文字認識の実行記録の記録を削除する。"
    return db.execute(
        "operations/indexing/shared/sql/ocr_runs_delete.sql",
        {"organization_id": organization_id, "id": id},
    )


def ocr_runs_get(db: Database, organization_id: str, id: str) -> list[OcrRunsRow]:
    "現在の組織に属する指定の文字認識の実行記録について、認識結果の保存先・検証用ハッシュ・確認状態を取得する。"
    return db.query(
        "operations/indexing/shared/sql/ocr_runs_get.sql",
        {"organization_id": organization_id, "id": id},
        OcrRunsRow,
    )


def ocr_runs_list(db: Database, organization_id: str) -> list[OcrRunsRow]:
    "現在の組織に属する文字認識の実行記録を識別子順に一覧取得する。"
    return db.query(
        "operations/indexing/shared/sql/ocr_runs_list.sql",
        {"organization_id": organization_id},
        OcrRunsRow,
    )


def outbox_get(db: Database, organization_id: str, id: str) -> list[OutboxRow]:
    "現在の組織に属する指定の反映・削除ジョブについて、対象文書と版・処理種別・進行状態・試行回数を取得する。"
    return db.query(
        "operations/indexing/shared/sql/outbox_get.sql",
        {"organization_id": organization_id, "id": id},
        OutboxRow,
    )


def outbox_update(db: Database, row: OutboxRow) -> int:
    "現在の組織に属する指定の反映・削除ジョブについて、対象文書と版・処理種別・進行状態・試行回数を更新する。"
    return db.execute("operations/indexing/shared/sql/outbox_update.sql", row.model_dump())


def versions_get(db: Database, organization_id: str, id: str) -> list[VersionsRow]:
    "現在の組織に属する指定の文書版について、確定した本文の保存先と画像構成・検証用ハッシュを取得する。"
    return db.query(
        "operations/indexing/shared/sql/versions_get.sql",
        {"organization_id": organization_id, "id": id},
        VersionsRow,
    )


def versions_list(db: Database, organization_id: str) -> list[VersionsRow]:
    "現在の組織に属する文書版を識別子順に一覧取得する。"
    return db.query(
        "operations/indexing/shared/sql/versions_list.sql",
        {"organization_id": organization_id},
        VersionsRow,
    )
