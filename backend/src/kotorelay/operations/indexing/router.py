"""indexingのAPIごとのルーターを登録する。"""

from fastapi import APIRouter

from kotorelay.operations.indexing.list_jobs.router import router as list_jobs
from kotorelay.operations.indexing.reconcile_index.router import router as reconcile_index
from kotorelay.operations.indexing.retry_job.router import router as retry_job

router = APIRouter()
router.include_router(retry_job)
router.include_router(list_jobs)
router.include_router(reconcile_index)
