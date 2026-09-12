"""サーバーの最新所属から操作権限と公開範囲を判定する。"""

from __future__ import annotations

import json
from datetime import UTC, datetime
from uuid import NAMESPACE_URL, uuid4, uuid5

from kotorelay.config import Settings
from kotorelay.db import Database
from kotorelay.errors import require
from kotorelay.generated import queries as q
from kotorelay.objects import Objects, digest
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
        self.db = db
        self.settings = settings
        self.objects = objects
        self.org = settings.organization_id
        organizations = q.organizations_get(db, self.org, self.org)
        require(bool(organizations) and not organizations[0].suspended, "unauthenticated", 401)
        self.organization = organizations[0]
        users = [u for u in q.users_list(db, self.org) if u.subject == subject and u.active]
        require(len(users) == 1, "unauthenticated", 401)
        self.user = users[0]
        active_depts = {d.id for d in q.departments_list(db, self.org) if d.active}
        self.memberships = [
            m
            for m in q.memberships_list(db, self.org)
            if m.user_id == self.user.id and m.active and m.department_id in active_depts
        ]

    def fence(self) -> None:
        require(q.organizations_fence(self.db, self.organization) == 1, "conflict", 409)

    def member(self, department_id: str) -> bool:
        return any(m.department_id == department_id for m in self.memberships)

    def permission(self, department_id: str, operation: str) -> bool:
        for m in self.memberships:
            if m.department_id == department_id:
                return {
                    "author": m.can_author,
                    "review": m.can_review,
                    "manage": m.leader,
                    "draft": m.can_author or m.can_review,
                }.get(operation, False)
        return False

    def can_read(self, doc: q.DocumentsRow) -> bool:
        if doc.status != "active" or not self.memberships:
            return False
        if doc.visibility == "organization":
            return True
        if self.member(doc.department_id):
            return True
        return doc.visibility == "selected" and any(
            self.member(department) for department in json.loads(doc.shared_departments)
        )

    def document(self, document_id: str, operation: str = "read") -> q.DocumentsRow:
        rows = q.documents_get(self.db, self.org, document_id)
        require(bool(rows))
        doc = rows[0]
        allowed = (
            self.can_read(doc)
            if operation == "read"
            else (doc.status != "deleted" and self.permission(doc.department_id, operation))
        )
        require(allowed)
        return doc

    def version(self, doc: q.DocumentsRow, version_id: str) -> q.VersionsRow:
        rows = q.versions_get(self.db, self.org, version_id)
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
            q.AuditRow(
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
        rows = q.idempotency_get(self.db, self.org, stable_id(self.user.id + key))
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
        q.idempotency_insert(
            self.db,
            q.IdempotencyRow(
                id=stable_id(self.user.id + key),
                organization_id=self.org,
                user_id=self.user.id,
                operation=operation,
                request_hash=digest(request.encode()),
                response=response,
            ),
        )
