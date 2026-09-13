"""correct_ocrのHTTP入力と業務処理の順序を宣言する。"""

from __future__ import annotations

from uuid import UUID

from fastapi import APIRouter

from kotorelay.operations.images.correct_ocr import functions as f
from kotorelay.operations.images.correct_ocr.contract import CONTRACT
from kotorelay.operations.images.correct_ocr.response_builders import build_response
from kotorelay.operations.images.correct_ocr.samples import SAMPLES
from kotorelay.operations.images.correct_ocr.schemas import OcrCorrection
from kotorelay.runtime import Ctx
from kotorelay.schemas import OcrResult

router = APIRouter(prefix="/api/images", tags=["画像・OCR"])


@router.post(
    "/{asset_id}/ocr",
    summary="OCRを訂正し新しいrunを保存",
    operation_id="correct_ocr",
    openapi_extra=CONTRACT.openapi_extra(SAMPLES),
)
def correct_ocr(ctx: Ctx, asset_id: UUID, data: OcrCorrection) -> dict[str, object]:
    assets = f.assets_get(ctx, asset_id)
    f.require_asset(assets)
    asset = assets[0]
    f.document_correct_ocr(ctx, asset)
    ids = f.select_ids(data)
    f.validate_region_ids(ids)
    for region in data.regions:
        f.validate_region_bounds(region)
    result = OcrResult(
        regions=f.select_result(data),
        engine="human-correction-v1",
        status="ready",
        confirmed=data.confirmed,
    )
    key = f.put_key(ctx, result)
    run = f.build_run(key, ctx, asset, result, data)
    f.ocr_runs_insert(ctx, run)
    f.record_correct_ocr_audit(ctx, asset)
    f.check_concurrent_access(ctx)
    return build_response(f.build_correct_ocr(run, result))
