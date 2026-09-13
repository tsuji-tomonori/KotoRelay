"""decide_reviewのHTTP入力と業務処理の順序を宣言する。"""

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
    return build_response(f.decide(ctx, str(submission_id), data, str(key)))
