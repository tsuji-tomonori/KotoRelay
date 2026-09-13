"""get_draftのHTTP入力と業務処理の順序を宣言する。"""

from uuid import UUID

from fastapi import APIRouter

from kotorelay.operations.documents.get_draft import functions as f
from kotorelay.operations.documents.get_draft.contract import CONTRACT
from kotorelay.operations.documents.get_draft.response_builders import build_response
from kotorelay.operations.documents.get_draft.samples import SAMPLES
from kotorelay.runtime import Ctx

router = APIRouter(prefix="/api/documents", tags=["文書"])


@router.get(
    "/{document_id}/draft",
    summary="下書きを取得",
    operation_id="get_draft",
    openapi_extra=CONTRACT.openapi_extra(SAMPLES),
)
def get_draft(ctx: Ctx, document_id: UUID) -> dict[str, object]:
    return build_response(f.draft(ctx, str(document_id)))
