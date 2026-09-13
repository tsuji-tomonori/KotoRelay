"""decide_reviewのHTTP入力と業務処理の順序を宣言する。"""

from __future__ import annotations

from uuid import UUID

from fastapi import APIRouter

from kotorelay.generated import models
from kotorelay.http_types import Key
from kotorelay.operations.reviews.decide_review import functions as f
from kotorelay.operations.reviews.decide_review.contract import CONTRACT
from kotorelay.operations.reviews.decide_review.response_builders import build_response
from kotorelay.operations.reviews.decide_review.samples import SAMPLES
from kotorelay.operations.reviews.decide_review.schemas import Decide
from kotorelay.runtime import Ctx

router = APIRouter(prefix="/api/reviews", tags=["審査"])


@router.post(
    "/{submission_id}/decision",
    summary="manifestを確認して承認・却下",
    operation_id="decide_review",
    openapi_extra=CONTRACT.openapi_extra(SAMPLES),
)
def decide_review(ctx: Ctx, submission_id: UUID, data: Decide, key: Key) -> models.SubmissionsRow:
    rows = f.submissions_get(ctx, submission_id)
    f.require_submission(rows)
    submission = rows[0]
    doc = f.document_doc(ctx, submission)
    request = str(submission_id) + data.model_dump_json()
    cached = f.find_previous_result(request, ctx, key)
    if cached:
        return build_response(f.build_decide_review(cached))
    f.require_pending_submission(submission)
    version = f.version_version(doc, ctx, submission)
    f.prevent_self_approval(version, ctx)
    f.validate_manifest_hash(submission, data, version)
    f.require_rejection_reason(data)
    updated = f.build_updated(submission, data, ctx)
    f.submissions_update(ctx, updated)
    if f.is_approved(data):
        previous = f.versions_get(ctx, doc.latest_version_id) if doc.latest_version_id else []
        if f.is_newer_publication(previous, version):
            f.documents_update(ctx, doc, version)
            f.outbox_insert(ctx, doc, version)
    f.record_decide_review_audit(ctx, doc, version, submission, updated, data)
    f.remember_decide_review_result(request, ctx, key, updated)
    f.check_concurrent_access(ctx)
    return build_response(updated)
