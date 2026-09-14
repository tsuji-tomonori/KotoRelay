"""get_imageのHTTP入力と業務処理の順序を宣言する。"""

from __future__ import annotations

from uuid import UUID

from fastapi import APIRouter
from fastapi.responses import Response

from kotorelay.operations.images.get_image import functions as f
from kotorelay.operations.images.get_image.contract import CONTRACT
from kotorelay.operations.images.get_image.response_builders import build_response
from kotorelay.operations.images.get_image.samples import SAMPLES
from kotorelay.operations.images.shared.functions import authorize_asset
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
    asset = authorize_asset(
        ctx, str(asset_id), str(version_id) if f.has_requested_version(version_id) else None
    )
    return build_response(f.get_get_image(asset, ctx))
