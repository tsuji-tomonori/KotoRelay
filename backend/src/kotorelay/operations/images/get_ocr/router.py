"""get_ocrのHTTP入力と業務処理の順序を宣言する。"""

from uuid import UUID

from fastapi import APIRouter

from kotorelay.operations.images.get_ocr import functions as f
from kotorelay.operations.images.get_ocr.contract import CONTRACT
from kotorelay.operations.images.get_ocr.response_builders import build_response
from kotorelay.operations.images.get_ocr.samples import SAMPLES
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
    return build_response(f.ocr(ctx, str(run_id), str(version_id) if version_id else None))
