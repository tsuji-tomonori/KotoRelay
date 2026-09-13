"""documentsのread_documentの業務判定と処理を実行する。"""

from __future__ import annotations

from kotorelay.context import Context
from kotorelay.errors import require
from kotorelay.operations.documents.read_document.generated import queries as q


def read_version(ctx: Context, document_id: str, version_id: str | None) -> dict[str, object]:
    rows = q.documents_get(ctx.db, ctx.org, document_id)
    require(bool(rows))
    doc = rows[0]
    require(doc.status != "deleted")
    require(ctx.can_read(doc) or ctx.permission(doc.department_id, "draft"))
    chosen = version_id or doc.latest_version_id
    require(chosen is not None)
    version = ctx.version(doc, str(chosen))
    return {
        "document": doc.model_copy(update={"title": version.title}),
        "version": version,
        "body": ctx.objects.get(version.body_key, version.body_hash).decode(),
        "index_ready": any(
            c.version_id == version.id and c.ready for c in q.chunks_list(ctx.db, ctx.org)
        ),
    }
