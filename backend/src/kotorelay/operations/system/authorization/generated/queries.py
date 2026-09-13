"""DDL・SQLから生成した型付き境界。直接編集しない。
SHA256: 5b9972f0208b6f468bc57c3567fcf8a12a60608b644bcd14ddf6c9828185c70b
"""

from kotorelay.db import Database
from kotorelay.generated.models import (
    AuditRow,
    DepartmentsRow,
    DocumentsRow,
    IdempotencyRow,
    MembershipsRow,
    OrganizationsRow,
    UsersRow,
    VersionsRow,
)


def audit_insert(db: Database, row: AuditRow) -> int:
    "現在の組織の監査記録として、操作した利用者・対象・変更前後の状態・理由を登録する。"
    return db.execute("operations/system/authorization/sql/audit_insert.sql", row.model_dump())


def departments_list(db: Database, organization_id: str) -> list[DepartmentsRow]:
    "現在の組織に属する部署を識別子順に一覧取得する。"
    return db.query(
        "operations/system/authorization/sql/departments_list.sql",
        {"organization_id": organization_id},
        DepartmentsRow,
    )


def documents_get(db: Database, organization_id: str, id: str) -> list[DocumentsRow]:
    "現在の組織に属する指定の文書について、文書の所有部署・公開範囲・状態・公開版の参照を取得する。"
    return db.query(
        "operations/system/authorization/sql/documents_get.sql",
        {"organization_id": organization_id, "id": id},
        DocumentsRow,
    )


def idempotency_get(db: Database, organization_id: str, id: str) -> list[IdempotencyRow]:
    "現在の組織に属する指定の再送判定の記録について、実行済み操作の入力ハッシュと応答を取得する。"
    return db.query(
        "operations/system/authorization/sql/idempotency_get.sql",
        {"organization_id": organization_id, "id": id},
        IdempotencyRow,
    )


def idempotency_insert(db: Database, row: IdempotencyRow) -> int:
    "現在の組織の操作の再送を判定するため、実行済み操作の入力ハッシュと応答を登録する。"
    return db.execute(
        "operations/system/authorization/sql/idempotency_insert.sql", row.model_dump()
    )


def memberships_list(db: Database, organization_id: str) -> list[MembershipsRow]:
    "現在の組織に属する部署所属を識別子順に一覧取得する。"
    return db.query(
        "operations/system/authorization/sql/memberships_list.sql",
        {"organization_id": organization_id},
        MembershipsRow,
    )


def organizations_fence(db: Database, row: OrganizationsRow) -> int:
    "組織の改訂番号が一致する場合だけ番号を進め、認可判定と権限失効の競合を検出する。"
    return db.execute(
        "operations/system/authorization/sql/organizations_fence.sql", row.model_dump()
    )


def organizations_get(db: Database, organization_id: str, id: str) -> list[OrganizationsRow]:
    "現在の組織の組織名・改訂番号・利用停止状態を取得する。"
    return db.query(
        "operations/system/authorization/sql/organizations_get.sql",
        {"organization_id": organization_id, "id": id},
        OrganizationsRow,
    )


def users_list(db: Database, organization_id: str) -> list[UsersRow]:
    "現在の組織に属する利用者を識別子順に一覧取得する。"
    return db.query(
        "operations/system/authorization/sql/users_list.sql",
        {"organization_id": organization_id},
        UsersRow,
    )


def versions_get(db: Database, organization_id: str, id: str) -> list[VersionsRow]:
    "現在の組織に属する指定の文書版について、確定した本文の保存先と画像構成・検証用ハッシュを取得する。"
    return db.query(
        "operations/system/authorization/sql/versions_get.sql",
        {"organization_id": organization_id, "id": id},
        VersionsRow,
    )
