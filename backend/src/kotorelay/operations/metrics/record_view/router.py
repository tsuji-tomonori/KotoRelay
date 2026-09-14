"""record_viewのHTTP入力と業務処理の順序を宣言する。"""

from __future__ import annotations

from uuid import UUID

from fastapi import APIRouter

from kotorelay.context import stable_id
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
    doc = f.document_doc(ctx, document_id)
    f.require_published_version(doc)
    f.require_consuming_membership(ctx, data)
    event_id = stable_id(ctx.user.id + data.id)
    previous = f.events_get(ctx, event_id)
    if f.has_previous_view(previous):
        f.validate_repeated_view(doc, data, previous)
        return build_response(f.build_record_view())
    f.events_insert(ctx, event_id, data, doc)
    f.check_concurrent_access(ctx)
    return build_response(f.build_record_view_2())
