"""groupsのchange_membershipの業務判定と処理を実行する。"""

from __future__ import annotations

import kotorelay.context as context_types
import kotorelay.generated.models as models
import kotorelay.operations.groups.change_membership.generated.queries as q
import kotorelay.operations.groups.change_membership.schemas as request_schemas
from kotorelay.context import new_id
from kotorelay.errors import require


def require_membership_management(
    ctx: context_types.Context, data: request_schemas.ChangeMembership
) -> None:
    """部署管理者または運用者による所属変更であることを確認する。"""
    return require(
        ctx.permission(data.department_id, "manage") or ctx.user.operator, "forbidden", 403
    )


def require_target_user(ctx: context_types.Context, data: request_schemas.ChangeMembership) -> None:
    """変更対象の利用者が同じ組織に存在することを確認する。"""
    return require(
        bool(q.users_get(ctx.db, q.UsersGetParams(organization_id=ctx.org, id=data.user_id))),
        "not_found",
        404,
    )


def require_target_department(
    ctx: context_types.Context, data: request_schemas.ChangeMembership
) -> None:
    """変更対象の部署が同じ組織に存在することを確認する。"""
    return require(
        bool(
            q.departments_get(
                ctx.db, q.DepartmentsGetParams(organization_id=ctx.org, id=data.department_id)
            )
        ),
        "not_found",
        404,
    )


def select_rows(
    ctx: context_types.Context, data: request_schemas.ChangeMembership
) -> list[q.MembershipsListRow]:
    """用途と対象に一致するデータだけを取り出す。"""
    return [
        m
        for m in q.memberships_list(ctx.db, q.MembershipsListParams(organization_id=ctx.org))
        if m.user_id == data.user_id and m.department_id == data.department_id
    ]


def build_row(
    rows: list[q.MembershipsListRow],
    ctx: context_types.Context,
    data: request_schemas.ChangeMembership,
) -> models.MembershipsRow:
    """後続処理に渡すデータを組み立てる。"""
    return models.MembershipsRow(
        id=rows[0].id if rows else new_id(), organization_id=ctx.org, **data.model_dump()
    )


def memberships_update(ctx: context_types.Context, row: models.MembershipsRow) -> int:
    """現在の組織に属する指定の部署所属について、所属部署・利用者・執筆や審査の権限・有効状態を更新する。"""
    return q.memberships_update(
        ctx.db, q.MembershipsUpdateParams.model_validate(row, from_attributes=True)
    )


def memberships_insert(ctx: context_types.Context, row: models.MembershipsRow) -> int:
    """現在の組織の利用者の部署所属を、所属部署・権限・有効状態を指定して登録する。"""
    return q.memberships_insert(
        ctx.db, q.MembershipsInsertParams.model_validate(row, from_attributes=True)
    )


def record_change_membership_audit(
    ctx: context_types.Context, rows: list[q.MembershipsListRow], row: models.MembershipsRow
) -> None:
    """実行した変更の対象と結果を監査記録へ追加する。"""
    return ctx.audit(
        "membership", before=str(rows[0].active) if rows else "", after=str(row.active)
    )


def check_concurrent_access(ctx: context_types.Context) -> None:
    """組織の更新競合を検出するための書込みフェンスを更新する。"""
    return ctx.fence()
