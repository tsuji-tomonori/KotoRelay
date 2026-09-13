"""reviewsのlist_reviewsの業務判定と処理を実行する。"""

from __future__ import annotations

import kotorelay.context as context_types
import kotorelay.operations.reviews.list_reviews.generated.queries as q


def map_documents(ctx: context_types.Context) -> dict[str, q.DocumentsListRow]:
    """取得したデータを識別子別に参照できる辞書へ変換する。"""
    return {
        d.id: d
        for d in q.documents_list(ctx.db, q.DocumentsListParams(organization_id=ctx.org))
        if d.status != "deleted"
        and (ctx.permission(d.department_id, "review") or ctx.permission(d.department_id, "manage"))
    }


def map_versions(ctx: context_types.Context) -> dict[str, q.VersionsListRow]:
    """取得したデータを識別子別に参照できる辞書へ変換する。"""
    return {v.id: v for v in q.versions_list(ctx.db, q.VersionsListParams(organization_id=ctx.org))}


def map_users(ctx: context_types.Context) -> dict[str, str]:
    """取得したデータを識別子別に参照できる辞書へ変換する。"""
    return {
        u.id: u.display_name
        for u in q.users_list(ctx.db, q.UsersListParams(organization_id=ctx.org))
    }


def map_departments(ctx: context_types.Context) -> dict[str, str]:
    """取得したデータを識別子別に参照できる辞書へ変換する。"""
    return {
        d.id: d.name
        for d in q.departments_list(ctx.db, q.DepartmentsListParams(organization_id=ctx.org))
    }


def select_list_reviews(
    users: dict[str, str],
    departments: dict[str, str],
    documents: dict[str, q.DocumentsListRow],
    versions: dict[str, q.VersionsListRow],
    ctx: context_types.Context,
) -> list[dict[str, object]]:
    """用途と対象に一致するデータだけを取り出す。"""
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
        for s in q.submissions_list(ctx.db, q.SubmissionsListParams(organization_id=ctx.org))
        if s.document_id in documents
    ]
