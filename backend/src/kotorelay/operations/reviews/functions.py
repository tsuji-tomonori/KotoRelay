"""特定manifestへの審査を冪等に確定し、最新承認版だけを公開する。"""

from __future__ import annotations

from kotorelay.context import Context, new_id, now
from kotorelay.errors import require
from kotorelay.generated import queries as q
from kotorelay.schemas import Decide


def list_reviews(ctx: Context) -> list[dict[str, object]]:
    documents = {
        d.id: d
        for d in q.documents_list(ctx.db, ctx.org)
        if d.status != "deleted"
        and (ctx.permission(d.department_id, "review") or ctx.permission(d.department_id, "manage"))
    }
    versions = {v.id: v for v in q.versions_list(ctx.db, ctx.org)}
    users = {u.id: u.display_name for u in q.users_list(ctx.db, ctx.org)}
    departments = {d.id: d.name for d in q.departments_list(ctx.db, ctx.org)}
    return [
        {
            "submission": s,
            "title": versions[s.version_id].title,
            "version_number": versions[s.version_id].number,
            "requested_by": users[s.requested_by],
            "department_name": departments[documents[s.document_id].department_id],
            "self_requested": s.requested_by == ctx.user.id,
            "can_review": ctx.permission(documents[s.document_id].department_id, "review"),
        }
        for s in q.submissions_list(ctx.db, ctx.org)
        if s.document_id in documents
    ]


def decide(ctx: Context, submission_id: str, data: Decide, key: str) -> q.SubmissionsRow:
    rows = q.submissions_get(ctx.db, ctx.org, submission_id)
    require(bool(rows))
    submission = rows[0]
    doc = ctx.document(submission.document_id, "review")
    request = submission_id + data.model_dump_json()
    cached = ctx.idempotent_result(key, "decide", request)
    if cached:
        return q.SubmissionsRow.model_validate_json(cached)
    require(submission.status == "pending", "conflict", 409)
    version = ctx.version(doc, submission.version_id)
    require(version.created_by != ctx.user.id, "self_approval", 403)
    require(
        submission.manifest_hash == data.manifest_hash == version.manifest_hash, "conflict", 409
    )
    require(data.decision != "rejected" or bool(data.reason.strip()), "reason_required", 422)
    updated = submission.model_copy(
        update={
            "status": data.decision,
            "reason": data.reason,
            "decided_by": ctx.user.id,
            "decided_at": now(),
        }
    )
    q.submissions_update(ctx.db, updated)
    if data.decision == "approved":
        previous = (
            q.versions_get(ctx.db, ctx.org, doc.latest_version_id) if doc.latest_version_id else []
        )
        if not previous or previous[0].number < version.number:
            q.documents_update(
                ctx.db,
                doc.model_copy(
                    update={
                        "latest_version_id": version.id,
                        "revision": doc.revision + 1,
                        "updated_at": now(),
                    }
                ),
            )
            q.outbox_insert(
                ctx.db,
                q.OutboxRow(
                    id=new_id(),
                    organization_id=ctx.org,
                    document_id=doc.id,
                    version_id=version.id,
                    kind="index",
                    status="pending",
                    attempts=0,
                    error_code="",
                    created_at=now(),
                ),
            )
    ctx.audit("review", doc.id, version.id, submission.status, updated.status, data.reason)
    ctx.remember(key, "decide", request, updated.model_dump_json())
    ctx.fence()
    return updated
