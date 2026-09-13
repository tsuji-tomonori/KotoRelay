"""groupsのlist_membersの業務判定と処理を実行する。"""

from __future__ import annotations

from kotorelay.context import Context
from kotorelay.errors import require
from kotorelay.operations.groups.list_members.generated import queries as q


def members(ctx: Context, department_id: str) -> list[dict[str, object]]:
    require(ctx.permission(department_id, "manage"), "forbidden", 403)
    users = {u.id: u for u in q.users_list(ctx.db, ctx.org)}
    return [
        {"membership": m, "display_name": users[m.user_id].display_name}
        for m in q.memberships_list(ctx.db, ctx.org)
        if m.department_id == department_id
    ]
