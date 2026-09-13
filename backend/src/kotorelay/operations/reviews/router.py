"""reviewsのAPIごとのルーターを登録する。"""

from fastapi import APIRouter

from kotorelay.operations.reviews.decide_review.router import router as decide_review
from kotorelay.operations.reviews.list_reviews.router import router as list_reviews

router = APIRouter()
router.include_router(list_reviews)
router.include_router(decide_review)
