"""documentsのlist_documentsの業務判定と処理を実行する。"""

from __future__ import annotations

from kotorelay.context import Context
from kotorelay.errors import require
from kotorelay.generated import models
from kotorelay.operations.documents.list_documents.generated import queries as q


def list_documents(
    ctx: Context,
    scope: str,
    offset: int,
    limit: int,
    search: str,
    department_id: str | None = None,
    status: str = "",
) -> list[models.DocumentsRow]:
    if department_id and scope in {"manage", "work"}:
        require(
            ctx.permission(department_id, "manage" if scope == "manage" else "draft"),
            "forbidden",
            403,
        )
    docs = (
        q.documents_by_department(ctx.db, ctx.org, department_id)
        if department_id
        else q.documents_list(ctx.db, ctx.org)
    )
    if scope == "manage":
        docs = [d for d in docs if ctx.permission(d.department_id, "manage")]
    elif scope == "work":
        docs = [
            d for d in docs if d.status != "deleted" and ctx.permission(d.department_id, "draft")
        ]
    else:
        docs = [d for d in docs if d.latest_version_id and ctx.can_read(d)]
        versions = {v.id: v for v in q.versions_list(ctx.db, ctx.org)}
        docs = [
            d.model_copy(update={"title": versions[d.latest_version_id].title})
            for d in docs
            if d.latest_version_id in versions
        ]
    docs = [
        d
        for d in docs
        if search.casefold() in d.title.casefold() and (not status or d.status == status)
    ]
    return sorted(docs, key=lambda d: d.updated_at, reverse=True)[offset : offset + limit]


def document_page(
    ctx: Context,
    scope: str,
    offset: int,
    limit: int,
    search: str,
    department_id: str | None,
    status: str,
) -> dict[str, object]:
    docs = list_documents(ctx, scope, offset, limit + 1, search, department_id, status)
    versions = {v.id: v for v in q.versions_list(ctx.db, ctx.org)}
    submissions = q.submissions_list(ctx.db, ctx.org)
    chunks = q.chunks_list(ctx.db, ctx.org)
    items = []
    for doc in docs[:limit]:
        version = versions.get(doc.latest_version_id or "")
        history = [s for s in submissions if s.document_id == doc.id]
        latest = max(history, key=lambda s: versions[s.version_id].number, default=None)
        approval = next((s for s in history if version and s.version_id == version.id), None)
        item = doc.model_dump()
        item.update(
            {
                "published_number": version.number if version else None,
                "approved_at": approval.decided_at if approval else None,
                "index_ready": bool(
                    version and any(c.version_id == version.id and c.ready for c in chunks)
                ),
                "summary": ctx.objects.get(version.body_key, version.body_hash).decode()[:180]
                if version and scope == "read"
                else "",
                "review_status": latest.status if latest and scope != "read" else None,
                "review_number": versions[latest.version_id].number
                if latest and scope != "read"
                else None,
            }
        )
        items.append(item)
    return {"items": items, "has_next": len(docs) > limit}
