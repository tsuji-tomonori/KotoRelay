"""indexingのreconcile_indexの業務判定と処理を実行する。"""

from __future__ import annotations

from kotorelay.context import Context
from kotorelay.errors import require
from kotorelay.operations.indexing.reconcile_index.generated import queries as q


def reconcile(ctx: Context) -> list[dict[str, str]]:
    require(ctx.user.operator, "forbidden", 403)
    chunks = q.chunks_list(ctx.db, ctx.org)
    differences: list[dict[str, str]] = []
    for doc in q.documents_list(ctx.db, ctx.org):
        current = [c for c in chunks if c.document_id == doc.id]
        if any(c.version_id != doc.latest_version_id or doc.status != "active" for c in current):
            differences.append({"document_id": doc.id, "reason": "旧版または停止済みの断片が残留"})
        if (
            doc.status == "active"
            and doc.latest_version_id
            and not any(c.version_id == doc.latest_version_id and c.ready for c in current)
        ):
            differences.append({"document_id": doc.id, "reason": "最新承認版が未反映"})
    return differences
