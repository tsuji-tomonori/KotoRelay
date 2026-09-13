"""metricsのAPIごとのルーターを登録する。"""

from fastapi import APIRouter

from kotorelay.operations.metrics.department_metrics.router import router as department_metrics
from kotorelay.operations.metrics.record_view.router import router as record_view

router = APIRouter()
router.include_router(record_view)
router.include_router(department_metrics)
