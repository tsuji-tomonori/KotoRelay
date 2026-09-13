"""upload_imageのHTTP入力と業務処理の順序を宣言する。"""

from __future__ import annotations

from uuid import UUID

from fastapi import APIRouter, UploadFile

from kotorelay.operations.images.upload_image import functions as f
from kotorelay.operations.images.upload_image.contract import CONTRACT
from kotorelay.operations.images.upload_image.response_builders import build_response
from kotorelay.operations.images.upload_image.samples import SAMPLES
from kotorelay.runtime import Ctx

router = APIRouter(prefix="/api/images", tags=["画像・OCR"])


@router.post(
    "/documents/{document_id}",
    status_code=201,
    summary="画像を添付して位置付きOCRを実行",
    operation_id="upload_image",
    openapi_extra=CONTRACT.openapi_extra(SAMPLES),
)
def upload_image(ctx: Ctx, document_id: UUID, file: UploadFile) -> dict[str, object]:
    doc = f.document_doc(ctx, document_id)
    assets = f.select_assets(ctx, doc)
    f.enforce_attachment_limit(assets, ctx)
    value, width, height = f.normalize_image(
        file.file.read(ctx.settings.max_image_bytes + 1),
        ctx.settings.max_image_bytes,
        ctx.settings.max_image_pixels,
    )
    key = f.put_key(value, ctx)
    asset = f.build_asset(key, width, height, ctx, doc, value)
    f.assets_insert(ctx, asset)
    result = f.run_ocr(value, width, height, ctx.settings.ocr_command)
    result_key = f.put_result_key(ctx, result)
    run = f.build_run(result_key, ctx, doc, asset, result)
    f.ocr_runs_insert(ctx, run)
    f.check_concurrent_access(ctx)
    return build_response(f.build_upload_image(asset, run, result))
