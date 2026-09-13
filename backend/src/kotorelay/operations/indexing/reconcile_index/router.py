"""reconcile_indexのHTTP入力と業務処理の順序を宣言する。"""

from fastapi import APIRouter

from kotorelay.operations.indexing.reconcile_index import functions as f
from kotorelay.operations.indexing.reconcile_index.contract import CONTRACT
from kotorelay.operations.indexing.reconcile_index.response_builders import build_response
from kotorelay.operations.indexing.reconcile_index.samples import SAMPLES
from kotorelay.runtime import Ctx

router = APIRouter(prefix="/api/operations", tags=["運用"])


@router.get(
    "/reconcile",
    summary="正本と索引の不一致を確認",
    operation_id="reconcile_index",
    openapi_extra=CONTRACT.openapi_extra(SAMPLES),
)
def reconcile_index(ctx: Ctx) -> list[dict[str, str]]:
    return build_response(f.reconcile(ctx))
