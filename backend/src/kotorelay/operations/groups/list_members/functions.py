"""groupsのlist_membersの業務判定と処理を実行する。"""

from __future__ import annotations

import uuid

import kotorelay.context as context_types
import kotorelay.operations.groups.list_members.generated.queries as q
from kotorelay.errors import require


def require_manager_permission(ctx: context_types.Context, department_id: uuid.UUID) -> None:
    """所属一覧を管理できる部署権限を確認する。"""
    return require(ctx.permission(str(department_id), "manage"), "forbidden", 403)


def map_users(ctx: context_types.Context) -> dict[str, q.UsersListRow]:
    """取得したデータを識別子別に参照できる辞書へ変換する。"""
    return {u.id: u for u in q.users_list(ctx.db, q.UsersListParams(organization_id=ctx.org))}


def select_list_members(
    users: dict[str, q.UsersListRow], ctx: context_types.Context, department_id: uuid.UUID
) -> list[dict[str, object]]:
    """用途と対象に一致するデータだけを取り出す。"""
    return [
        {"membership": m, "display_name": users[m.user_id].display_name}
        for m in q.memberships_list(ctx.db, q.MembershipsListParams(organization_id=ctx.org))
        if m.department_id == str(department_id)
    ]
