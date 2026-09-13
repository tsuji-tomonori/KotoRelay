"""groupsのget_identityの業務判定と処理を実行する。"""

from __future__ import annotations

import kotorelay.context as context_types
from kotorelay.operations.groups.get_identity.generated import queries as q


def build_get_identity(ctx: context_types.Context) -> dict[str, object]:
    """後続処理に渡すデータを組み立てる。"""
    return {
        "user": ctx.user,
        "memberships": ctx.memberships,
        "departments": [
            d
            for d in q.departments_list(ctx.db, q.DepartmentsListParams(organization_id=ctx.org))
            if ctx.member(d.id)
        ],
        "directory": [
            d
            for d in q.departments_list(ctx.db, q.DepartmentsListParams(organization_id=ctx.org))
            if d.active
        ],
        "mode": ctx.settings.mode,
    }
