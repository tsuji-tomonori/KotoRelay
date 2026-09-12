"""審査APIを公開する。"""

from uuid import UUID

from fastapi import APIRouter

from kotorelay.generated import queries as q
from kotorelay.operations.documents.router import Key
from kotorelay.operations.reviews import functions as f
from kotorelay.runtime import Ctx
from kotorelay.schemas import Decide

router = APIRouter(prefix="/api/reviews", tags=["審査"])


@router.get("", summary="審査状況を一覧", operation_id="list_reviews")
def list_reviews(ctx: Ctx) -> list[dict[str, object]]:
    return f.list_reviews(ctx)


@router.post(
    "/{submission_id}/decision",
    summary="manifestを確認して承認・却下",
    operation_id="decide_review",
)
def decide_review(ctx: Ctx, submission_id: UUID, data: Decide, key: Key) -> q.SubmissionsRow:
    return f.decide(ctx, str(submission_id), data, str(key))
