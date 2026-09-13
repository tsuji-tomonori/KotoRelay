"""get_imageのHTTP入力と業務処理の順序を宣言する。"""

from uuid import UUID

from fastapi import APIRouter
from fastapi.responses import Response

from kotorelay.operations.images.get_image import functions as f
from kotorelay.operations.images.get_image.contract import CONTRACT
from kotorelay.operations.images.get_image.response_builders import build_response
from kotorelay.operations.images.get_image.samples import SAMPLES
from kotorelay.runtime import Ctx

router = APIRouter(prefix="/api/images", tags=["画像・OCR"])


@router.get(
    "/{asset_id}",
    summary="現在の認可で画像を配信",
    operation_id="get_image",
    response_class=Response,
    openapi_extra=CONTRACT.openapi_extra(SAMPLES),
)
def get_image(ctx: Ctx, asset_id: UUID, version_id: UUID | None = None) -> Response:
    return build_response(f.image(ctx, str(asset_id), str(version_id) if version_id else None))
