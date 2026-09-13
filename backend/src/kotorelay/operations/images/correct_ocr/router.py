"""correct_ocrのHTTP入力と業務処理の順序を宣言する。"""

from uuid import UUID

from fastapi import APIRouter

from kotorelay.operations.images.correct_ocr import functions as f
from kotorelay.operations.images.correct_ocr.contract import CONTRACT
from kotorelay.operations.images.correct_ocr.response_builders import build_response
from kotorelay.operations.images.correct_ocr.samples import SAMPLES
from kotorelay.operations.images.correct_ocr.schemas import OcrCorrection
from kotorelay.runtime import Ctx

router = APIRouter(prefix="/api/images", tags=["画像・OCR"])


@router.post(
    "/{asset_id}/ocr",
    summary="OCRを訂正し新しいrunを保存",
    operation_id="correct_ocr",
    openapi_extra=CONTRACT.openapi_extra(SAMPLES),
)
def correct_ocr(ctx: Ctx, asset_id: UUID, data: OcrCorrection) -> dict[str, object]:
    return build_response(f.correct(ctx, str(asset_id), data))
