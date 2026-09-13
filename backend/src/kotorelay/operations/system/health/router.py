"""healthのHTTP入力と業務処理の順序を宣言する。"""

from __future__ import annotations

from fastapi import APIRouter

from kotorelay.operations.system.health import functions as f
from kotorelay.operations.system.health.contract import CONTRACT
from kotorelay.operations.system.health.response_builders import build_response
from kotorelay.operations.system.health.samples import SAMPLES

router = APIRouter(prefix="/api", tags=["システム"])


@router.get(
    "/health",
    summary="死活確認",
    operation_id="health",
    openapi_extra=CONTRACT.openapi_extra(SAMPLES),
)
def health() -> dict[str, str]:
    """外部依存へ接続せずプロセスの稼働状態を返す。"""
    return build_response(f.build_health())
