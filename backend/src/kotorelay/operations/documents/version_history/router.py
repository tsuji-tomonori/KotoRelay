"""version_historyのHTTP入力と業務処理の順序を宣言する。"""

from uuid import UUID

from fastapi import APIRouter

from kotorelay.operations.documents.version_history import functions as f
from kotorelay.operations.documents.version_history.contract import CONTRACT
from kotorelay.operations.documents.version_history.response_builders import build_response
from kotorelay.operations.documents.version_history.samples import SAMPLES
from kotorelay.runtime import Ctx

router = APIRouter(prefix="/api/documents", tags=["文書"])


@router.get(
    "/{document_id}/history",
    summary="担当文書の版履歴",
    operation_id="version_history",
    openapi_extra=CONTRACT.openapi_extra(SAMPLES),
)
def version_history(ctx: Ctx, document_id: UUID) -> list[dict[str, object]]:
    return build_response(f.history(ctx, str(document_id)))
