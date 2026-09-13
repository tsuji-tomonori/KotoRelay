"""imagesのAPIごとのルーターを登録する。"""

from fastapi import APIRouter

from kotorelay.operations.images.correct_ocr.router import router as correct_ocr
from kotorelay.operations.images.get_image.router import router as get_image
from kotorelay.operations.images.get_ocr.router import router as get_ocr
from kotorelay.operations.images.upload_image.router import router as upload_image

router = APIRouter()
router.include_router(upload_image)
router.include_router(get_image)
router.include_router(get_ocr)
router.include_router(correct_ocr)
