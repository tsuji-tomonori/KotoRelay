"""systemのAPIごとのルーターを登録する。"""

from fastapi import APIRouter

from kotorelay.operations.system.health.router import router as health

router = APIRouter()
router.include_router(health)
