"""version_diffのHTTP入力と業務処理の順序を宣言する。"""

from uuid import UUID

from fastapi import APIRouter

from kotorelay.operations.documents.version_diff import functions as f
from kotorelay.operations.documents.version_diff.contract import CONTRACT
from kotorelay.operations.documents.version_diff.response_builders import build_response
from kotorelay.operations.documents.version_diff.samples import SAMPLES
from kotorelay.runtime import Ctx

router = APIRouter(prefix="/api/documents", tags=["文書"])


@router.get(
    "/{document_id}/diff",
    summary="版IDを指定して本文差分を比較",
    operation_id="version_diff",
    openapi_extra=CONTRACT.openapi_extra(SAMPLES),
)
def version_diff(ctx: Ctx, document_id: UUID, left: UUID, right: UUID) -> dict[str, str]:
    return build_response(f.diff(ctx, str(document_id), str(left), str(right)))
