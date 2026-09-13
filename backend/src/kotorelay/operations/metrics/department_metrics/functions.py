"""metricsのdepartment_metricsの業務判定と処理を実行する。"""

from __future__ import annotations

from datetime import datetime
from zoneinfo import ZoneInfo

from kotorelay.context import Context, now
from kotorelay.errors import require
from kotorelay.operations.metrics.department_metrics.generated import queries as q


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
