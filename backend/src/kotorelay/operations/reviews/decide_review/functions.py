"""reviewsのdecide_reviewの業務判定と処理を実行する。"""

from __future__ import annotations

from kotorelay.context import Context, new_id, now
from kotorelay.errors import require
from kotorelay.generated import models
from kotorelay.operations.reviews.decide_review.generated import queries as q
from kotorelay.operations.reviews.decide_review.schemas import Decide


def decide(ctx: Context, submission_id: str, data: Decide, key: str) -> models.SubmissionsRow:
    rows = q.submissions_get(ctx.db, ctx.org, submission_id)
    require(bool(rows))
    submission = rows[0]
    doc = ctx.document(submission.document_id, "review")
    request = submission_id + data.model_dump_json()
    cached = ctx.idempotent_result(key, "decide", request)
    if cached:
        return models.SubmissionsRow.model_validate_json(cached)
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
                models.OutboxRow(
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
