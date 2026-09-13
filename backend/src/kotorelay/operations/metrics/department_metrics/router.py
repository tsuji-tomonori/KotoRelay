"""department_metricsのHTTP入力と業務処理の順序を宣言する。"""

from datetime import datetime
from uuid import UUID

from fastapi import APIRouter

from kotorelay.operations.metrics.department_metrics import functions as f
from kotorelay.operations.metrics.department_metrics.contract import CONTRACT
from kotorelay.operations.metrics.department_metrics.response_builders import build_response
from kotorelay.operations.metrics.department_metrics.samples import SAMPLES
from kotorelay.runtime import Ctx

router = APIRouter(prefix="/api/metrics", tags=["利用統計"])


@router.get(
    "/{department_id}",
    summary="部署の利用数と文書貢献を集計",
    operation_id="department_metrics",
    openapi_extra=CONTRACT.openapi_extra(SAMPLES),
)
def department_metrics(
    ctx: Ctx, department_id: UUID, start: datetime, end: datetime
) -> dict[str, object]:
    return build_response(f.summary(ctx, str(department_id), start, end))
