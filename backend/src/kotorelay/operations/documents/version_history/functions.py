"""documentsのversion_historyの業務判定と処理を実行する。"""

from __future__ import annotations

from kotorelay.context import Context
from kotorelay.operations.documents.version_history.generated import queries as q


def history(ctx: Context, document_id: str) -> list[dict[str, object]]:
    doc = ctx.document(document_id, "draft")
    submissions = {s.version_id: s for s in q.submissions_list(ctx.db, ctx.org)}
    return [
        {"version": v, "submission": submissions.get(v.id)}
        for v in sorted(q.versions_list(ctx.db, ctx.org), key=lambda v: v.number, reverse=True)
        if v.document_id == doc.id
    ]
