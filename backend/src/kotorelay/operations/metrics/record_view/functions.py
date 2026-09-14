"""metricsのrecord_viewの業務判定と処理を実行する。"""

from __future__ import annotations

import uuid

import kotorelay.context as context_types
import kotorelay.generated.models as models
import kotorelay.operations.metrics.record_view.generated.queries as q
import kotorelay.operations.metrics.record_view.schemas as request_schemas
from kotorelay.context import now
from kotorelay.errors import require


def document_doc(ctx: context_types.Context, document_id: uuid.UUID) -> models.DocumentsRow:
    """文書を取得して要求された操作の権限を確認する。"""
    return ctx.document(str(document_id))


def require_published_version(doc: models.DocumentsRow) -> None:
    """閲覧対象に公開中の承認版が存在することを確認する。"""
    return require(bool(doc.latest_version_id))


def require_consuming_membership(
    ctx: context_types.Context, data: request_schemas.ViewEvent
) -> None:
    """閲覧の帰属先部署への所属を確認する。"""
    return require(ctx.member(data.department_id), "forbidden", 403)


def events_get(ctx: context_types.Context, event_id: str) -> list[q.EventsGetRow]:
    """現在の組織に属する指定の利用イベントについて、利用者・帰属部署・閲覧や質問の対象・結果・発生日時を取得する。"""
    return q.events_get(ctx.db, q.EventsGetParams(organization_id=ctx.org, id=event_id))


def validate_repeated_view(
    doc: models.DocumentsRow, data: request_schemas.ViewEvent, previous: list[q.EventsGetRow]
) -> None:
    """同じ冪等キーの閲覧対象と帰属部署が一致することを確認する。"""
    return require(
        previous[0].document_id == doc.id
        and previous[0].department_id == data.department_id
        and (previous[0].kind == "view"),
        "idempotency_conflict",
        409,
    )


def build_record_view() -> dict[str, bool]:
    """後続処理に渡すデータを組み立てる。"""
    return {"recorded": False}


def events_insert(
    ctx: context_types.Context,
    event_id: str,
    data: request_schemas.ViewEvent,
    doc: models.DocumentsRow,
) -> int:
    """現在の組織の利用イベントとして、利用者・帰属部署・閲覧や質問の対象・結果・発生日時を登録する。"""
    return q.events_insert(
        ctx.db,
        q.EventsInsertParams(
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


def check_concurrent_access(ctx: context_types.Context) -> None:
    """組織の更新競合を検出するための書込みフェンスを更新する。"""
    return ctx.fence()


def build_record_view_2() -> dict[str, bool]:
    """後続処理に渡すデータを組み立てる。"""
    return {"recorded": True}


def has_previous_view(rows: list[q.EventsGetRow]) -> bool:
    """同じ閲覧イベントが既に記録されている。"""
    return bool(rows)
