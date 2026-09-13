"""metricsのrecord_viewの業務判定と処理を実行する。"""

from __future__ import annotations

from kotorelay.context import Context, now, stable_id
from kotorelay.errors import require
from kotorelay.generated import models
from kotorelay.operations.metrics.record_view.generated import queries as q
from kotorelay.operations.metrics.record_view.schemas import ViewEvent


def view(ctx: Context, document_id: str, data: ViewEvent) -> dict[str, bool]:
    doc = ctx.document(document_id)
    require(bool(doc.latest_version_id))
    require(ctx.member(data.department_id), "forbidden", 403)
    event_id = stable_id(ctx.user.id + data.id)
    previous = q.events_get(ctx.db, ctx.org, event_id)
    if previous:
        require(
            previous[0].document_id == doc.id
            and previous[0].department_id == data.department_id
            and previous[0].kind == "view",
            "idempotency_conflict",
            409,
        )
        return {"recorded": False}
    q.events_insert(
        ctx.db,
        models.EventsRow(
            id=event_id,
            organization_id=ctx.org,
            user_id=ctx.user.id,
            department_id=data.department_id,
            document_id=doc.id,
            answer_id=None,
            kind="view",
            outcome="viewed",
            created_at=now(),
        ),
    )
    ctx.fence()
    return {"recorded": True}
