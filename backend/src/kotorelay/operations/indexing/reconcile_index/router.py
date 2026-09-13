"""reconcile_indexのHTTP入力と業務処理の順序を宣言する。"""

from __future__ import annotations

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
    f.require_operator(ctx)
    chunks = f.chunks_list(ctx)
    differences: list[dict[str, str]] = []
    for doc in f.documents_list(ctx):
        current = f.select_current(chunks, doc)
        if f.has_outdated_chunks(current, doc):
            differences.append(f.build_reconcile_index(doc))
        if f.needs_index_repair(doc, current):
            differences.append(f.build_reconcile_index_2(doc))
    return build_response(differences)
