"""record_viewのHTTP入力と業務処理の順序を宣言する。"""

from uuid import UUID

from fastapi import APIRouter

from kotorelay.operations.metrics.record_view import functions as f
from kotorelay.operations.metrics.record_view.contract import CONTRACT
from kotorelay.operations.metrics.record_view.response_builders import build_response
from kotorelay.operations.metrics.record_view.samples import SAMPLES
from kotorelay.operations.metrics.record_view.schemas import ViewEvent
from kotorelay.runtime import Ctx

router = APIRouter(prefix="/api/metrics", tags=["利用統計"])


@router.post(
    "/views/{document_id}",
    summary="実閲覧を一意IDで記録",
    operation_id="record_view",
    openapi_extra=CONTRACT.openapi_extra(SAMPLES),
)
def record_view(ctx: Ctx, document_id: UUID, data: ViewEvent) -> dict[str, bool]:
    return build_response(f.view(ctx, str(document_id), data))
