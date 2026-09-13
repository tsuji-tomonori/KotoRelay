"""upload_imageのHTTP入力と業務処理の順序を宣言する。"""

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
    return build_response(
        f.upload(ctx, str(document_id), file.file.read(ctx.settings.max_image_bytes + 1))
    )
