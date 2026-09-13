"""save_draftのHTTP入力と業務処理の順序を宣言する。"""

from __future__ import annotations

from uuid import UUID

from fastapi import APIRouter

from kotorelay.operations.documents.save_draft import functions as f
from kotorelay.operations.documents.save_draft.contract import CONTRACT
from kotorelay.operations.documents.save_draft.response_builders import build_response
from kotorelay.operations.documents.save_draft.samples import SAMPLES
from kotorelay.operations.documents.save_draft.schemas import SaveDraft
from kotorelay.operations.documents.shared import functions as draft_functions
from kotorelay.runtime import Ctx

router = APIRouter(prefix="/api/documents", tags=["文書"])


@router.put(
    "/{document_id}/draft",
    summary="競合を検出して下書きを保存",
    operation_id="save_draft",
    openapi_extra=CONTRACT.openapi_extra(SAMPLES),
)
def save_draft(ctx: Ctx, document_id: UUID, data: SaveDraft) -> dict[str, object]:
    doc = f.document_doc(ctx, document_id)
    row = next(d for d in f.drafts_list(ctx) if d.document_id == doc.id)
    f.validate_draft_revision(row, data)
    f.validate_placements(ctx, doc, data)
    key = f.put_key(ctx, data)
    f.drafts_update(ctx, row, key, data)
    f.documents_update(ctx, doc, data)
    f.check_concurrent_access(ctx)
    current_document = draft_functions.authorize_draft(ctx, str(document_id))
    current_draft = draft_functions.load_draft_row(ctx, current_document.id)
    body = draft_functions.load_draft_body(ctx, current_draft)
    return build_response(draft_functions.build_draft_data(current_document, current_draft, body))
