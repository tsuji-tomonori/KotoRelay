"""save_draftのHTTP入力と業務処理の順序を宣言する。"""

from uuid import UUID

from fastapi import APIRouter

from kotorelay.operations.documents.save_draft import functions as f
from kotorelay.operations.documents.save_draft.contract import CONTRACT
from kotorelay.operations.documents.save_draft.response_builders import build_response
from kotorelay.operations.documents.save_draft.samples import SAMPLES
from kotorelay.operations.documents.save_draft.schemas import SaveDraft
from kotorelay.runtime import Ctx

router = APIRouter(prefix="/api/documents", tags=["文書"])


@router.put(
    "/{document_id}/draft",
    summary="競合を検出して下書きを保存",
    operation_id="save_draft",
    openapi_extra=CONTRACT.openapi_extra(SAMPLES),
)
def save_draft(ctx: Ctx, document_id: UUID, data: SaveDraft) -> dict[str, object]:
    return build_response(f.save(ctx, str(document_id), data))
