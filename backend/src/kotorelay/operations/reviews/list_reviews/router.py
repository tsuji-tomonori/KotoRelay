"""list_reviewsのHTTP入力と業務処理の順序を宣言する。"""

from fastapi import APIRouter

from kotorelay.operations.reviews.list_reviews import functions as f
from kotorelay.operations.reviews.list_reviews.contract import CONTRACT
from kotorelay.operations.reviews.list_reviews.response_builders import build_response
from kotorelay.operations.reviews.list_reviews.samples import SAMPLES
from kotorelay.runtime import Ctx

router = APIRouter(prefix="/api/reviews", tags=["審査"])


@router.get(
    "",
    summary="審査状況を一覧",
    operation_id="list_reviews",
    openapi_extra=CONTRACT.openapi_extra(SAMPLES),
)
def list_reviews(ctx: Ctx) -> list[dict[str, object]]:
    return build_response(f.list_reviews(ctx))
