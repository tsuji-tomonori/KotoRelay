"""閲覧と部署統計のAPIを公開する。"""

from datetime import datetime
from uuid import UUID

from fastapi import APIRouter

from kotorelay.operations.metrics import functions as f
from kotorelay.runtime import Ctx
from kotorelay.schemas import ViewEvent

router = APIRouter(prefix="/api/metrics", tags=["利用統計"])


@router.post("/views/{document_id}", summary="実閲覧を一意IDで記録", operation_id="record_view")
def record_view(ctx: Ctx, document_id: UUID, data: ViewEvent) -> dict[str, bool]:
    return f.view(ctx, str(document_id), data)


@router.get(
    "/{department_id}", summary="部署の利用数と文書貢献を集計", operation_id="department_metrics"
)
def department_metrics(
    ctx: Ctx, department_id: UUID, start: datetime, end: datetime
) -> dict[str, object]:
    return f.summary(ctx, str(department_id), start, end)
