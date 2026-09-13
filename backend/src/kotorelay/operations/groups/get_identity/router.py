"""get_identityのHTTP入力と業務処理の順序を宣言する。"""

from fastapi import APIRouter

from kotorelay.operations.groups.get_identity import functions as f
from kotorelay.operations.groups.get_identity.contract import CONTRACT
from kotorelay.operations.groups.get_identity.response_builders import build_response
from kotorelay.operations.groups.get_identity.samples import SAMPLES
from kotorelay.runtime import Ctx

router = APIRouter(prefix="/api/groups", tags=["部署"])


@router.get(
    "/me",
    summary="本人と現在の所属権限を取得",
    operation_id="get_identity",
    openapi_extra=CONTRACT.openapi_extra(SAMPLES),
)
def get_identity(ctx: Ctx) -> dict[str, object]:
    return build_response(f.identity(ctx))
