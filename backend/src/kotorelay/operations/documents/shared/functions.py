"""documentsのsharedの業務判定と処理を実行する。"""

from __future__ import annotations

import json

from kotorelay.context import Context
from kotorelay.operations.documents.shared.generated import queries as q


def draft(ctx: Context, document_id: str) -> dict[str, object]:
    doc = ctx.document(document_id, "draft")
    row = next(d for d in q.drafts_list(ctx.db, ctx.org) if d.document_id == doc.id)
    return {
        "document": doc,
        "body": ctx.objects.get(row.body_key, row.body_hash).decode(),
        "revision": row.revision,
        "placements": json.loads(row.placements),
    }
