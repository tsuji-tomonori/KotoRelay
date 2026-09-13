"""metricsのdepartment_metricsの業務判定と処理を実行する。"""

from __future__ import annotations

import datetime as datetime_module
import uuid
from zoneinfo import ZoneInfo

import kotorelay.context as context_types
import kotorelay.operations.metrics.department_metrics.generated.queries as q
from kotorelay.context import now
from kotorelay.errors import require


def require_manager_permission(ctx: context_types.Context, department_id: uuid.UUID) -> None:
    """集計対象部署の管理権限を確認する。"""
    return require(ctx.permission(str(department_id), "manage"), "forbidden", 403)


def require_period_timezone(start: datetime_module.datetime, end: datetime_module.datetime) -> None:
    """集計期間の開始と終了にタイムゾーンがあることを確認する。"""
    return require(start.tzinfo is not None and end.tzinfo is not None, "invalid_period", 422)


def validate_period_order(start: datetime_module.datetime, end: datetime_module.datetime) -> None:
    """集計開始日時が終了日時より前であることを確認する。"""
    return require(start < end, "invalid_period", 422)


def select_events(
    start: datetime_module.datetime, end: datetime_module.datetime, ctx: context_types.Context
) -> list[q.EventsListRow]:
    """用途と対象に一致するデータだけを取り出す。"""
    return [
        e
        for e in q.events_list(ctx.db, q.EventsListParams(organization_id=ctx.org))
        if start <= e.created_at < end
    ]


def select_consumed(
    events: list[q.EventsListRow], department_id: uuid.UUID
) -> list[q.EventsListRow]:
    """用途と対象に一致するデータだけを取り出す。"""
    return [e for e in events if e.department_id == str(department_id)]


def select_docs(ctx: context_types.Context, department_id: uuid.UUID) -> list[q.DocumentsListRow]:
    """用途と対象に一致するデータだけを取り出す。"""
    return [
        d
        for d in q.documents_list(ctx.db, q.DocumentsListParams(organization_id=ctx.org))
        if d.department_id == str(department_id)
    ]


def build_department_metrics(
    start: datetime_module.datetime,
    end: datetime_module.datetime,
    department_id: uuid.UUID,
    docs: list[q.DocumentsListRow],
    consumed: list[q.EventsListRow],
    events: list[q.EventsListRow],
) -> dict[str, object]:
    """後続処理に渡すデータを組み立てる。"""
    return {
        "department_id": str(department_id),
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
