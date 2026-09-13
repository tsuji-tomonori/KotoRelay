"""groupsのchange_membershipの業務判定と処理を実行する。"""

from __future__ import annotations

from kotorelay.context import Context, new_id
from kotorelay.errors import require
from kotorelay.generated import models
from kotorelay.operations.groups.change_membership.generated import queries as q
from kotorelay.operations.groups.change_membership.schemas import ChangeMembership


def change(ctx: Context, data: ChangeMembership) -> models.MembershipsRow:
    require(ctx.permission(data.department_id, "manage") or ctx.user.operator, "forbidden", 403)
    require(bool(q.users_get(ctx.db, ctx.org, data.user_id)), "not_found", 404)
    require(bool(q.departments_get(ctx.db, ctx.org, data.department_id)), "not_found", 404)
    rows = [
        m
        for m in q.memberships_list(ctx.db, ctx.org)
        if m.user_id == data.user_id and m.department_id == data.department_id
    ]
    row = models.MembershipsRow(
        id=rows[0].id if rows else new_id(), organization_id=ctx.org, **data.model_dump()
    )
    if rows:
        q.memberships_update(ctx.db, row)
    else:
        q.memberships_insert(ctx.db, row)
    ctx.audit("membership", before=str(rows[0].active) if rows else "", after=str(row.active))
    ctx.fence()
    return row
