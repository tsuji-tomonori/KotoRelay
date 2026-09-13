"""list_jobsのHTTP入力と業務処理の順序を宣言する。"""

from fastapi import APIRouter

from kotorelay.operations.indexing.list_jobs import functions as f
from kotorelay.operations.indexing.list_jobs.contract import CONTRACT
from kotorelay.operations.indexing.list_jobs.response_builders import build_response
from kotorelay.operations.indexing.list_jobs.samples import SAMPLES
from kotorelay.runtime import Ctx

router = APIRouter(prefix="/api/operations", tags=["運用"])


@router.get(
    "/jobs",
    summary="反映ジョブと失敗理由を確認",
    operation_id="list_jobs",
    openapi_extra=CONTRACT.openapi_extra(SAMPLES),
)
def list_jobs(ctx: Ctx, details: bool = False) -> list[dict[str, object]]:
    return build_response(f.list_jobs(ctx, details))
