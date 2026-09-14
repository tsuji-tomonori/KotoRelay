"""get_ocrのHTTP入力と業務処理の順序を宣言する。"""

from __future__ import annotations

from typing import cast
from uuid import UUID

from fastapi import APIRouter

from kotorelay.operations.images.get_ocr import functions as f
from kotorelay.operations.images.get_ocr.contract import CONTRACT
from kotorelay.operations.images.get_ocr.response_builders import build_response
from kotorelay.operations.images.get_ocr.samples import SAMPLES
from kotorelay.operations.images.shared.functions import authorize_asset
from kotorelay.runtime import Ctx
from kotorelay.schemas import OcrResult

router = APIRouter(prefix="/api/images", tags=["画像・OCR"])


@router.get(
    "/ocr/{run_id}",
    summary="認可されたOCR領域を取得",
    operation_id="get_ocr",
    openapi_extra=CONTRACT.openapi_extra(SAMPLES),
)
def get_ocr(ctx: Ctx, run_id: UUID, version_id: UUID | None = None) -> OcrResult:
    rows = f.ocr_runs_get(ctx, run_id)
    f.require_ocr_run(rows)
    run = rows[0]
    asset = authorize_asset(
        ctx, run.asset_id, str(version_id) if f.has_requested_version(version_id) else None
    )
    if f.has_requested_version(version_id):
        doc = f.documents_get(ctx, asset)[0]
        version = f.version_version(doc, ctx, cast(UUID, version_id))
        f.validate_version_ocr(run, version)
    result = f.build_result(run, ctx)
    return build_response(f.build_get_ocr(result, run))
