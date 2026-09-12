"""運用者によるoutboxの確認・再処理を公開する。"""

from uuid import UUID

from fastapi import APIRouter

from kotorelay.generated import queries as q
from kotorelay.operations.indexing import functions as f
from kotorelay.runtime import Ctx, Rt

router = APIRouter(prefix="/api/operations", tags=["運用"])


@router.get("/jobs", summary="反映ジョブと失敗理由を確認", operation_id="list_jobs")
def list_jobs(ctx: Ctx, details: bool = False) -> list[dict[str, object]]:
    return f.job_details(ctx) if details else [row.model_dump() for row in f.jobs(ctx)]


@router.post("/jobs/{job_id}", summary="反映ジョブを再処理", operation_id="retry_job")
def retry_job(ctx: Ctx, rt: Rt, job_id: UUID) -> q.OutboxRow:
    return f.process(ctx, rt.engine, str(job_id))


@router.get("/reconcile", summary="正本と索引の不一致を確認", operation_id="reconcile_index")
def reconcile_index(ctx: Ctx) -> list[dict[str, str]]:
    return f.reconcile(ctx)
