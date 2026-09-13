"""retry_jobのHTTP入力と業務処理の順序を宣言する。"""

from uuid import UUID

from fastapi import APIRouter

from kotorelay.generated import models
from kotorelay.operations.indexing.retry_job import functions as f
from kotorelay.operations.indexing.retry_job.contract import CONTRACT
from kotorelay.operations.indexing.retry_job.response_builders import build_response
from kotorelay.operations.indexing.retry_job.samples import SAMPLES
from kotorelay.runtime import Ctx, Rt

router = APIRouter(prefix="/api/operations", tags=["運用"])


@router.post(
    "/jobs/{job_id}",
    summary="反映ジョブを再処理",
    operation_id="retry_job",
    openapi_extra=CONTRACT.openapi_extra(SAMPLES),
)
def retry_job(ctx: Ctx, rt: Rt, job_id: UUID) -> models.OutboxRow:
    return build_response(f.retry(ctx, rt.engine, str(job_id)))
