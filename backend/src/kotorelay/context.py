"""サーバーの最新所属から操作権限と公開範囲を判定する。"""

from __future__ import annotations

import json
from datetime import UTC, datetime
from uuid import NAMESPACE_URL, uuid4, uuid5

from kotorelay.config import Settings
from kotorelay.db import Database
from kotorelay.errors import require
from kotorelay.generated import models
from kotorelay.objects import Objects, digest
from kotorelay.operations.system.authorization.functions import is_read_operation
from kotorelay.operations.system.authorization.generated import queries as q
from kotorelay.schemas import Manifest


def now() -> datetime:
    return datetime.now(UTC)


def new_id() -> str:
    return str(uuid4())


def stable_id(value: str) -> str:
    return str(uuid5(NAMESPACE_URL, "kotorelay:" + value))


def serialized(value: object) -> str:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


class Context:
    def __init__(self, db: Database, settings: Settings, objects: Objects, subject: str):
        """有効な組織と利用者を確認し、最新の所属を読み込む。"""
        self.db = db
        self.settings = settings
        self.objects = objects
        self.org = settings.organization_id
        organizations = q.organizations_get(
            db, q.OrganizationsGetParams(organization_id=self.org, id=self.org)
        )
        require(bool(organizations) and (not organizations[0].suspended), "unauthenticated", 401)
        self.organization = organizations[0]
        users = [
            u
            for u in q.users_list(db, q.UsersListParams(organization_id=self.org))
            if u.subject == subject and u.active
        ]
        require(len(users) == 1, "unauthenticated", 401)
        self.user = users[0]
        active_depts = {
            d.id
            for d in q.departments_list(db, q.DepartmentsListParams(organization_id=self.org))
            if d.active
        }
        self.memberships = [
            m
            for m in q.memberships_list(db, q.MembershipsListParams(organization_id=self.org))
            if m.user_id == self.user.id and m.active and (m.department_id in active_depts)
        ]

    def fence(self) -> None:
        """処理中に組織の状態が変更されていないことを確認する。"""
        require(
            q.organizations_fence(
                self.db,
                q.OrganizationsFenceParams.model_validate(self.organization, from_attributes=True),
            )
            == 1,
            "conflict",
            409,
        )

    def member(self, department_id: str) -> bool:
        """指定した部署に現在も所属している。"""
        return any(m.department_id == department_id for m in self.memberships)

    def permission(self, department_id: str, operation: str) -> bool:
        """指定した部署で要求された操作を実行できる。"""
        for m in self.memberships:
            if m.department_id == department_id:
                return {
                    "author": m.can_author,
                    "review": m.can_review,
                    "manage": m.leader,
                    "draft": m.can_author or m.can_review,
                }.get(operation, False)
        return False

    def can_read(self, doc: models.DocumentsRow) -> bool:
        """現在の所属と公開範囲で文書を閲覧できる。"""
        if doc.status != "active" or not self.memberships:
            return False
        if doc.visibility == "organization":
            return True
        if self.member(doc.department_id):
            return True
        return doc.visibility == "selected" and any(
            self.member(department) for department in json.loads(doc.shared_departments)
        )

    def document(self, document_id: str, operation: str = "read") -> models.DocumentsRow:
        """対象の文書が存在し、要求された操作を実行できることを確認する。"""
        rows = q.documents_get(
            self.db, q.DocumentsGetParams(organization_id=self.org, id=document_id)
        )
        require(bool(rows))
        doc = rows[0]
        allowed = (
            self.can_read(doc)
            if is_read_operation(operation)
            else doc.status != "deleted" and self.permission(doc.department_id, operation)
        )
        require(allowed)
        return doc

    def version(self, doc: models.DocumentsRow, version_id: str) -> models.VersionsRow:
        """文書の版が存在し、閲覧権限と実体の整合性が有効なことを確認する。"""
        rows = q.versions_get(self.db, q.VersionsGetParams(organization_id=self.org, id=version_id))
        require(bool(rows) and rows[0].document_id == doc.id)
        version = rows[0]
        if not self.permission(doc.department_id, "draft"):
            require(self.can_read(doc) and doc.latest_version_id == version.id)
        require(digest(version.manifest.encode()) == version.manifest_hash, "integrity", 503)
        Manifest.model_validate_json(version.manifest)
        return version

    def audit(
        self,
        action: str,
        document_id: str | None = None,
        version_id: str | None = None,
        before: str = "",
        after: str = "",
        reason: str = "",
    ) -> None:
        q.audit_insert(
            self.db,
            q.AuditInsertParams(
                id=new_id(),
                organization_id=self.org,
                user_id=self.user.id,
                document_id=document_id,
                version_id=version_id,
                action=action,
                before_state=before,
                after_state=after,
                reason=reason,
                created_at=now(),
            ),
        )

    def idempotent_result(self, key: str, operation: str, request: str) -> str | None:
        """同じ冪等キーの処理内容が一致することを確認して保存済み応答を返す。"""
        rows = q.idempotency_get(
            self.db,
            q.IdempotencyGetParams(organization_id=self.org, id=stable_id(self.user.id + key)),
        )
        if not rows:
            return None
        record = rows[0]
        require(
            record.operation == operation and record.request_hash == digest(request.encode()),
            "idempotency_conflict",
            409,
        )
        return record.response

    def remember(self, key: str, operation: str, request: str, response: str) -> None:
        """冪等キーに処理内容と応答を保存する。"""
        q.idempotency_insert(
            self.db,
            q.IdempotencyInsertParams(
                id=stable_id(self.user.id + key),
                organization_id=self.org,
                user_id=self.user.id,
                operation=operation,
                request_hash=digest(request.encode()),
                response=response,
            ),
        )
