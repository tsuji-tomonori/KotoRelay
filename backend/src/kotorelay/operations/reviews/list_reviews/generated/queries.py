"""DDL・SQLから生成した型付き境界。直接編集しない。
SHA256: ed55fdba04faa27e897fbd0d7982c5133f472f06d84718577e2499dd84477cdc
"""

from kotorelay.db import Database
from kotorelay.generated.models import (
    DepartmentsRow,
    DocumentsRow,
    SubmissionsRow,
    UsersRow,
    VersionsRow,
)


def departments_list(db: Database, organization_id: str) -> list[DepartmentsRow]:
    "現在の組織に属する部署を識別子順に一覧取得する。"
    return db.query(
        "operations/reviews/list_reviews/sql/departments_list.sql",
        {"organization_id": organization_id},
        DepartmentsRow,
    )


def documents_list(db: Database, organization_id: str) -> list[DocumentsRow]:
    "現在の組織に属する文書を識別子順に一覧取得する。"
    return db.query(
        "operations/reviews/list_reviews/sql/documents_list.sql",
        {"organization_id": organization_id},
        DocumentsRow,
    )


def submissions_list(db: Database, organization_id: str) -> list[SubmissionsRow]:
    "現在の組織に属する承認申請を識別子順に一覧取得する。"
    return db.query(
        "operations/reviews/list_reviews/sql/submissions_list.sql",
        {"organization_id": organization_id},
        SubmissionsRow,
    )


def users_list(db: Database, organization_id: str) -> list[UsersRow]:
    "現在の組織に属する利用者を識別子順に一覧取得する。"
    return db.query(
        "operations/reviews/list_reviews/sql/users_list.sql",
        {"organization_id": organization_id},
        UsersRow,
    )


def versions_list(db: Database, organization_id: str) -> list[VersionsRow]:
    "現在の組織に属する文書版を識別子順に一覧取得する。"
    return db.query(
        "operations/reviews/list_reviews/sql/versions_list.sql",
        {"organization_id": organization_id},
        VersionsRow,
    )
