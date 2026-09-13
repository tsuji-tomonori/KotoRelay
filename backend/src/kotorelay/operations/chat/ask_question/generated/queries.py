"""DDL・SQLから生成した型付き境界。直接編集しない。
SHA256: 23563c43e5278a00671ddf3eadd51598430e9e42620a1085bb8df8dd3023e2c4
"""

from kotorelay.db import Database
from kotorelay.generated.models import (
    AnswersRow,
    AssetsRow,
    ChunksRow,
    ConversationsRow,
    DocumentsRow,
    EventsRow,
    VersionsRow,
)


def answers_get(db: Database, organization_id: str, id: str) -> list[AnswersRow]:
    "現在の組織に属する指定の回答履歴について、質問・回答の保存先と根拠・回答状態を取得する。"
    return db.query(
        "operations/chat/ask_question/sql/answers_get.sql",
        {"organization_id": organization_id, "id": id},
        AnswersRow,
    )


def answers_insert(db: Database, row: AnswersRow) -> int:
    "現在の組織の回答履歴として、質問者・利用部署・質問と回答の保存先・根拠を登録する。"
    return db.execute("operations/chat/ask_question/sql/answers_insert.sql", row.model_dump())


def answers_list(db: Database, organization_id: str) -> list[AnswersRow]:
    "現在の組織に属する回答履歴を識別子順に一覧取得する。"
    return db.query(
        "operations/chat/ask_question/sql/answers_list.sql",
        {"organization_id": organization_id},
        AnswersRow,
    )


def assets_get(db: Database, organization_id: str, id: str) -> list[AssetsRow]:
    "現在の組織に属する指定の添付画像について、画像の保存先・形式・寸法・検証用ハッシュを取得する。"
    return db.query(
        "operations/chat/ask_question/sql/assets_get.sql",
        {"organization_id": organization_id, "id": id},
        AssetsRow,
    )


def chunks_list(db: Database, organization_id: str) -> list[ChunksRow]:
    "現在の組織に属する検索用の文書断片を識別子順に一覧取得する。"
    return db.query(
        "operations/chat/ask_question/sql/chunks_list.sql",
        {"organization_id": organization_id},
        ChunksRow,
    )


def conversations_get(db: Database, organization_id: str, id: str) -> list[ConversationsRow]:
    "現在の組織に属する指定の会話について、会話の所有者と開始日時を取得する。"
    return db.query(
        "operations/chat/ask_question/sql/conversations_get.sql",
        {"organization_id": organization_id, "id": id},
        ConversationsRow,
    )


def conversations_insert(db: Database, row: ConversationsRow) -> int:
    "現在の組織の会話を、所有者と開始日時を指定して登録する。"
    return db.execute("operations/chat/ask_question/sql/conversations_insert.sql", row.model_dump())


def documents_list(db: Database, organization_id: str) -> list[DocumentsRow]:
    "現在の組織に属する文書を識別子順に一覧取得する。"
    return db.query(
        "operations/chat/ask_question/sql/documents_list.sql",
        {"organization_id": organization_id},
        DocumentsRow,
    )


def events_insert(db: Database, row: EventsRow) -> int:
    "現在の組織の利用イベントとして、利用者・帰属部署・閲覧や質問の対象・結果・発生日時を登録する。"
    return db.execute("operations/chat/ask_question/sql/events_insert.sql", row.model_dump())


def events_list(db: Database, organization_id: str) -> list[EventsRow]:
    "現在の組織に属する利用イベントを識別子順に一覧取得する。"
    return db.query(
        "operations/chat/ask_question/sql/events_list.sql",
        {"organization_id": organization_id},
        EventsRow,
    )


def versions_get(db: Database, organization_id: str, id: str) -> list[VersionsRow]:
    "現在の組織に属する指定の文書版について、確定した本文の保存先と画像構成・検証用ハッシュを取得する。"
    return db.query(
        "operations/chat/ask_question/sql/versions_get.sql",
        {"organization_id": organization_id, "id": id},
        VersionsRow,
    )
