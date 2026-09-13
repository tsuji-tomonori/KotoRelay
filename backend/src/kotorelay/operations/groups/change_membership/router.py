"""change_membershipのHTTP入力と業務処理の順序を宣言する。"""

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
    return build_response(f.change(ctx, data))
