"""一意イベントから部署の消費と所有文書の貢献を分離して集計する。"""

from datetime import datetime
from zoneinfo import ZoneInfo

from kotorelay.context import Context, now, stable_id
from kotorelay.errors import require
from kotorelay.generated import queries as q
from kotorelay.schemas import ViewEvent


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
        q.EventsRow(
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


def summary(ctx: Context, department_id: str, start: datetime, end: datetime) -> dict[str, object]:
    require(ctx.permission(department_id, "manage"), "forbidden", 403)
    require(start.tzinfo is not None and end.tzinfo is not None, "invalid_period", 422)
    require(start < end, "invalid_period", 422)
    events = [e for e in q.events_list(ctx.db, ctx.org) if start <= e.created_at < end]
    consumed = [e for e in events if e.department_id == department_id]
    docs = [d for d in q.documents_list(ctx.db, ctx.org) if d.department_id == department_id]
    return {
        "department_id": department_id,
        "timezone": "Asia/Tokyo",
        "generated_at": now().astimezone(ZoneInfo("Asia/Tokyo")),
        "start": start,
        "end": end,
        "questions": sum(e.kind == "question" for e in consumed),
        "views": sum(e.kind == "view" for e in consumed),
        "unique_viewers": len({e.user_id for e in consumed if e.kind == "view"}),
        "outcomes": {
            status: sum(e.kind == "outcome" and e.outcome == status for e in consumed)
            for status in ["answered", "held", "failed", "cancelled"]
        },
        "documents": [
            {
                "id": d.id,
                "title": d.title,
                "views": sum(e.kind == "view" and e.document_id == d.id for e in events),
                "contributions": len(
                    {
                        e.answer_id
                        for e in events
                        if e.kind == "contribution" and e.document_id == d.id
                    }
                ),
            }
            for d in docs
        ],
    }
