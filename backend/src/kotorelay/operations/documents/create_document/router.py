"""create_documentのHTTP入力と業務処理の順序を宣言する。"""

from __future__ import annotations

from fastapi import APIRouter

from kotorelay.generated import models
from kotorelay.operations.documents.create_document import functions as f
from kotorelay.operations.documents.create_document.contract import CONTRACT
from kotorelay.operations.documents.create_document.response_builders import build_response
from kotorelay.operations.documents.create_document.samples import SAMPLES
from kotorelay.operations.documents.create_document.schemas import CreateDocument
from kotorelay.runtime import Ctx

router = APIRouter(prefix="/api/documents", tags=["文書"])


@router.post(
    "",
    status_code=201,
    summary="文書を作成",
    operation_id="create_document",
    openapi_extra=CONTRACT.openapi_extra(SAMPLES),
)
def create_document(ctx: Ctx, data: CreateDocument) -> models.DocumentsRow:
    f.require_author_permission(ctx, data)
    doc = f.initialize_document(ctx, data)
    f.documents_insert(ctx, doc)
    key = f.save_empty_body(ctx)
    f.drafts_insert(ctx, key, doc)
    f.record_create_document_audit(ctx, doc)
    f.check_concurrent_access(ctx)
    return build_response(doc)
