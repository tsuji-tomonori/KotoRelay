"""reviewsのlist_reviewsの業務判定と処理を実行する。"""

from __future__ import annotations

from kotorelay.context import Context
from kotorelay.operations.reviews.list_reviews.generated import queries as q


def list_reviews(ctx: Context) -> list[dict[str, object]]:
    documents = {
        d.id: d
        for d in q.documents_list(ctx.db, ctx.org)
        if d.status != "deleted"
        and (ctx.permission(d.department_id, "review") or ctx.permission(d.department_id, "manage"))
    }
    versions = {v.id: v for v in q.versions_list(ctx.db, ctx.org)}
    users = {u.id: u.display_name for u in q.users_list(ctx.db, ctx.org)}
    departments = {d.id: d.name for d in q.departments_list(ctx.db, ctx.org)}
    return [
        {
            "submission": s,
            "title": versions[s.version_id].title,
            "version_number": versions[s.version_id].number,
            "requested_by": users[s.requested_by],
            "department_name": departments[documents[s.document_id].department_id],
            "self_requested": s.requested_by == ctx.user.id,
            "can_review": ctx.permission(documents[s.document_id].department_id, "review"),
        }
        for s in q.submissions_list(ctx.db, ctx.org)
        if s.document_id in documents
    ]
