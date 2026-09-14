"""list_jobsのHTTP入力と業務処理の順序を宣言する。"""

from __future__ import annotations

from fastapi import APIRouter

from kotorelay.generated import models
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
    """要求された詳細度に合わせて運用者向けジョブ一覧を取得する。"""
    f.require_operator(ctx)
    rows: list[models.OutboxRow] = list(f.outbox_list(ctx))
    if f.requests_details(details):
        docs = f.map_docs(ctx)
        versions = f.map_versions(ctx)
        return build_response(f.select_job_details(rows, docs, versions))
    return build_response(f.select_list_jobs(rows))
