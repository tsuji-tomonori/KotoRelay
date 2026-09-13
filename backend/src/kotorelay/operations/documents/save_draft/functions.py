"""documentsのsave_draftの業務判定と処理を実行する。"""

from __future__ import annotations

import json

from kotorelay.context import Context, now
from kotorelay.errors import require
from kotorelay.generated import models
from kotorelay.operations.documents.save_draft.generated import queries as q
from kotorelay.operations.documents.save_draft.schemas import SaveDraft
from kotorelay.operations.documents.shared.functions import draft


def save(ctx: Context, document_id: str, data: SaveDraft) -> dict[str, object]:
    doc = ctx.document(document_id, "author")
    row = next(d for d in q.drafts_list(ctx.db, ctx.org) if d.document_id == doc.id)
    require(row.revision == data.revision, "conflict", 409)
    validate_placements(ctx, doc, data)
    key = ctx.objects.put(data.body.encode(), "text/markdown")
    q.drafts_update(
        ctx.db,
        row.model_copy(
            update={
                "body_key": key,
                "body_hash": key,
                "revision": row.revision + 1,
                "updated_by": ctx.user.id,
                "placements": json.dumps([p.model_dump() for p in data.placements]),
            }
        ),
    )
    q.documents_update(
        ctx.db,
        doc.model_copy(
            update={"title": data.title, "revision": doc.revision + 1, "updated_at": now()}
        ),
    )
    ctx.fence()
    return draft(ctx, doc.id)


def validate_placements(ctx: Context, doc: models.DocumentsRow, data: SaveDraft) -> None:
    require(len({p.id for p in data.placements}) == len(data.placements), "invalid_placement", 422)
    for placement in data.placements:
        assets = q.assets_get(ctx.db, ctx.org, placement.asset_id)
        runs = q.ocr_runs_get(ctx.db, ctx.org, placement.ocr_run_id)
        require(bool(assets) and bool(runs), "invalid_placement", 422)
        require(
            assets[0].document_id == doc.id
            and runs[0].asset_id == assets[0].id
            and runs[0].document_id == doc.id
            and placement.offset <= len(data.body),
            "invalid_placement",
            422,
        )
