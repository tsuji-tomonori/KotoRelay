"""認可付き画像とOCRのAPIを公開する。"""

from uuid import UUID

from fastapi import APIRouter, UploadFile
from fastapi.responses import Response

from kotorelay.operations.images import functions as f
from kotorelay.runtime import Ctx
from kotorelay.schemas import OcrCorrection, OcrResult

router = APIRouter(prefix="/api/images", tags=["画像・OCR"])


@router.post(
    "/documents/{document_id}",
    status_code=201,
    summary="画像を添付して位置付きOCRを実行",
    operation_id="upload_image",
)
def upload_image(ctx: Ctx, document_id: UUID, file: UploadFile) -> dict[str, object]:
    return f.upload(ctx, str(document_id), file.file.read(ctx.settings.max_image_bytes + 1))


@router.get(
    "/{asset_id}",
    summary="現在の認可で画像を配信",
    operation_id="get_image",
    response_class=Response,
)
def get_image(ctx: Ctx, asset_id: UUID, version_id: UUID | None = None) -> Response:
    return Response(
        f.image(ctx, str(asset_id), str(version_id) if version_id else None), media_type="image/png"
    )


@router.post("/{asset_id}/ocr", summary="OCRを訂正し新しいrunを保存", operation_id="correct_ocr")
def correct_ocr(ctx: Ctx, asset_id: UUID, data: OcrCorrection) -> dict[str, object]:
    return f.correct(ctx, str(asset_id), data)


@router.get("/ocr/{run_id}", summary="認可されたOCR領域を取得", operation_id="get_ocr")
def get_ocr(ctx: Ctx, run_id: UUID, version_id: UUID | None = None) -> OcrResult:
    return f.ocr(ctx, str(run_id), str(version_id) if version_id else None)
