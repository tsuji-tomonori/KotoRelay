"""DDL・SQLから生成した型付き境界。直接編集しない。
SHA256: a874dcb8846a217994572fc3adbafbc4c22cb4e0f806451e686f56cf908479b3
"""

from kotorelay.db import Database
from kotorelay.generated.models import (
    ChunksRow,
    DocumentsRow,
    SubmissionsRow,
    VersionsRow,
)


def chunks_list(db: Database, organization_id: str) -> list[ChunksRow]:
    "現在の組織に属する検索用の文書断片を識別子順に一覧取得する。"
    return db.query(
        "operations/documents/list_documents/sql/chunks_list.sql",
        {"organization_id": organization_id},
        ChunksRow,
    )


def documents_by_department(
    db: Database, organization_id: str, department_id: str
) -> list[DocumentsRow]:
    "現在の組織に属する文書を指定した所有部署で絞り込み、一覧の対象を取得する。"
    return db.query(
        "operations/documents/list_documents/sql/documents_by_department.sql",
        {"organization_id": organization_id, "department_id": department_id},
        DocumentsRow,
    )


def documents_list(db: Database, organization_id: str) -> list[DocumentsRow]:
    "現在の組織に属する文書を識別子順に一覧取得する。"
    return db.query(
        "operations/documents/list_documents/sql/documents_list.sql",
        {"organization_id": organization_id},
        DocumentsRow,
    )


def submissions_list(db: Database, organization_id: str) -> list[SubmissionsRow]:
    "現在の組織に属する承認申請を識別子順に一覧取得する。"
    return db.query(
        "operations/documents/list_documents/sql/submissions_list.sql",
        {"organization_id": organization_id},
        SubmissionsRow,
    )


def versions_list(db: Database, organization_id: str) -> list[VersionsRow]:
    "現在の組織に属する文書版を識別子順に一覧取得する。"
    return db.query(
        "operations/documents/list_documents/sql/versions_list.sql",
        {"organization_id": organization_id},
        VersionsRow,
    )
