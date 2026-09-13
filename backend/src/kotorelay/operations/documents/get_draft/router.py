"""get_draftのHTTP入力と業務処理の順序を宣言する。"""

from __future__ import annotations

from uuid import UUID

from fastapi import APIRouter

from kotorelay.operations.documents.get_draft.contract import CONTRACT
from kotorelay.operations.documents.get_draft.response_builders import build_response
from kotorelay.operations.documents.get_draft.samples import SAMPLES
from kotorelay.operations.documents.shared import functions as draft_functions
from kotorelay.runtime import Ctx

router = APIRouter(prefix="/api/documents", tags=["文書"])


@router.get(
    "/{document_id}/draft",
    summary="下書きを取得",
    operation_id="get_draft",
    openapi_extra=CONTRACT.openapi_extra(SAMPLES),
)
def get_draft(ctx: Ctx, document_id: UUID) -> dict[str, object]:
    """担当権限を検証して下書きの本文と配置を取得する。"""
    current_document = draft_functions.authorize_draft(ctx, str(document_id))
    current_draft = draft_functions.load_draft_row(ctx, current_document.id)
    body = draft_functions.load_draft_body(ctx, current_draft)
    return build_response(draft_functions.build_draft_data(current_document, current_draft, body))
