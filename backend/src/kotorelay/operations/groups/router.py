"""現在の本人・部署所属APIを公開する。"""

from uuid import UUID

from fastapi import APIRouter

from kotorelay.generated import queries as q
from kotorelay.operations.groups import functions as f
from kotorelay.runtime import Ctx
from kotorelay.schemas import ChangeMembership

router = APIRouter(prefix="/api/groups", tags=["部署"])


@router.get("/me", summary="本人と現在の所属権限を取得", operation_id="get_identity")
def get_identity(ctx: Ctx) -> dict[str, object]:
    return f.identity(ctx)


@router.get("/{department_id}/members", summary="自部署の所属を一覧", operation_id="list_members")
def list_members(ctx: Ctx, department_id: UUID) -> list[dict[str, object]]:
    return f.members(ctx, str(department_id))


@router.put("/memberships", summary="部署の所属権限を変更", operation_id="change_membership")
def change_membership(ctx: Ctx, data: ChangeMembership) -> q.MembershipsRow:
    return f.change(ctx, data)
