"""list_membersのHTTP入力と業務処理の順序を宣言する。"""

from uuid import UUID

from fastapi import APIRouter

from kotorelay.operations.groups.list_members import functions as f
from kotorelay.operations.groups.list_members.contract import CONTRACT
from kotorelay.operations.groups.list_members.response_builders import build_response
from kotorelay.operations.groups.list_members.samples import SAMPLES
from kotorelay.runtime import Ctx

router = APIRouter(prefix="/api/groups", tags=["部署"])


@router.get(
    "/{department_id}/members",
    summary="自部署の所属を一覧",
    operation_id="list_members",
    openapi_extra=CONTRACT.openapi_extra(SAMPLES),
)
def list_members(ctx: Ctx, department_id: UUID) -> list[dict[str, object]]:
    return build_response(f.members(ctx, str(department_id)))
