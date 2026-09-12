"""部署所属と権限を管理し、認証トークンから権限を推測しない。"""

from kotorelay.context import Context, new_id
from kotorelay.errors import require
from kotorelay.generated import queries as q
from kotorelay.schemas import ChangeMembership


def identity(ctx: Context) -> dict[str, object]:
    return {
        "user": ctx.user,
        "memberships": ctx.memberships,
        "departments": [d for d in q.departments_list(ctx.db, ctx.org) if ctx.member(d.id)],
        "mode": ctx.settings.mode,
    }


def members(ctx: Context, department_id: str) -> list[dict[str, object]]:
    require(ctx.permission(department_id, "manage"), "forbidden", 403)
    users = {u.id: u for u in q.users_list(ctx.db, ctx.org)}
    return [
        {"membership": m, "display_name": users[m.user_id].display_name}
        for m in q.memberships_list(ctx.db, ctx.org)
        if m.department_id == department_id
    ]


def change(ctx: Context, data: ChangeMembership) -> q.MembershipsRow:
    require(ctx.permission(data.department_id, "manage") or ctx.user.operator, "forbidden", 403)
    require(bool(q.users_get(ctx.db, ctx.org, data.user_id)), "not_found", 404)
    require(bool(q.departments_get(ctx.db, ctx.org, data.department_id)), "not_found", 404)
    rows = [
        m
        for m in q.memberships_list(ctx.db, ctx.org)
        if m.user_id == data.user_id and m.department_id == data.department_id
    ]
    row = q.MembershipsRow(
        id=rows[0].id if rows else new_id(), organization_id=ctx.org, **data.model_dump()
    )
    if rows:
        q.memberships_update(ctx.db, row)
    else:
        q.memberships_insert(ctx.db, row)
    ctx.audit("membership", before=str(rows[0].active) if rows else "", after=str(row.active))
    ctx.fence()
    return row
