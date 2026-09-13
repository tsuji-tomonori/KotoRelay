"""groupsのget_identityの業務判定と処理を実行する。"""

from __future__ import annotations

from kotorelay.context import Context
from kotorelay.operations.groups.get_identity.generated import queries as q


def identity(ctx: Context) -> dict[str, object]:
    return {
        "user": ctx.user,
        "memberships": ctx.memberships,
        "departments": [d for d in q.departments_list(ctx.db, ctx.org) if ctx.member(d.id)],
        "directory": [d for d in q.departments_list(ctx.db, ctx.org) if d.active],
        "mode": ctx.settings.mode,
    }
