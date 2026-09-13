"""read_documentのHTTP入力と業務処理の順序を宣言する。"""

from uuid import UUID

from fastapi import APIRouter

from kotorelay.operations.documents.read_document import functions as f
from kotorelay.operations.documents.read_document.contract import CONTRACT
from kotorelay.operations.documents.read_document.response_builders import build_response
from kotorelay.operations.documents.read_document.samples import SAMPLES
from kotorelay.runtime import Ctx

router = APIRouter(prefix="/api/documents", tags=["文書"])


@router.get(
    "/{document_id}",
    summary="承認版または担当版を表示",
    operation_id="read_document",
    openapi_extra=CONTRACT.openapi_extra(SAMPLES),
)
def read_document(ctx: Ctx, document_id: UUID, version_id: UUID | None = None) -> dict[str, object]:
    return build_response(
        f.read_version(ctx, str(document_id), str(version_id) if version_id else None)
    )
