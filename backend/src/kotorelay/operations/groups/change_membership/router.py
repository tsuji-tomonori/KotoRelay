"""change_membershipのHTTP入力と業務処理の順序を宣言する。"""

from __future__ import annotations

from fastapi import APIRouter

from kotorelay.generated import models
from kotorelay.operations.groups.change_membership import functions as f
from kotorelay.operations.groups.change_membership.contract import CONTRACT
from kotorelay.operations.groups.change_membership.response_builders import build_response
from kotorelay.operations.groups.change_membership.samples import SAMPLES
from kotorelay.operations.groups.change_membership.schemas import ChangeMembership
from kotorelay.runtime import Ctx

router = APIRouter(prefix="/api/groups", tags=["部署"])


@router.put(
    "/memberships",
    summary="部署の所属権限を変更",
    operation_id="change_membership",
    openapi_extra=CONTRACT.openapi_extra(SAMPLES),
)
def change_membership(ctx: Ctx, data: ChangeMembership) -> models.MembershipsRow:
    f.require_membership_management(ctx, data)
    f.require_target_user(ctx, data)
    f.require_target_department(ctx, data)
    rows = f.select_rows(ctx, data)
    row = f.build_row(rows, ctx, data)
    if rows:
        f.memberships_update(ctx, row)
    else:
        f.memberships_insert(ctx, row)
    f.record_change_membership_audit(ctx, rows, row)
    f.check_concurrent_access(ctx)
    return build_response(row)
