"""documentsのlist_documentsの業務判定と処理を実行する。"""

from __future__ import annotations

import typing

import kotorelay.context as context_types
import kotorelay.generated.models as models
import kotorelay.operations.documents.list_documents.generated.queries as q
from kotorelay.errors import require


def requires_department_permission(department_id: str | None, scope: str) -> bool:
    """部署指定の管理用または執筆用の一覧かを判定する。"""
    return bool(department_id and scope in {"manage", "work"})


def require_department_permission(
    department_id: str, ctx: context_types.Context, scope: str
) -> None:
    """指定した一覧の用途に対応する部署権限を確認する。"""
    return require(
        ctx.permission(department_id, "manage" if scope == "manage" else "draft"), "forbidden", 403
    )


def documents_by_department(
    ctx: context_types.Context, department_id: str
) -> list[q.DocumentsByDepartmentRow]:
    """現在の組織に属する文書を指定した所有部署で絞り込み、一覧の対象を取得する。"""
    return q.documents_by_department(
        ctx.db, q.DocumentsByDepartmentParams(organization_id=ctx.org, department_id=department_id)
    )


def documents_list(ctx: context_types.Context) -> list[q.DocumentsListRow]:
    """現在の組織に属する文書を識別子順に一覧取得する。"""
    return q.documents_list(ctx.db, q.DocumentsListParams(organization_id=ctx.org))


def is_management_scope(scope: str) -> bool:
    """管理用の文書一覧を要求しているかを判定する。"""
    return bool(scope == "manage")


def select_docs(
    docs: list[models.DocumentsRow], ctx: context_types.Context
) -> list[models.DocumentsRow]:
    """用途と対象に一致するデータだけを取り出す。"""
    return [d for d in docs if ctx.permission(d.department_id, "manage")]


def is_authoring_scope(scope: str) -> bool:
    """執筆用の文書一覧を要求しているかを判定する。"""
    return bool(scope == "work")


def select_docs_2(
    docs: list[models.DocumentsRow], ctx: context_types.Context
) -> list[models.DocumentsRow]:
    """用途と対象に一致するデータだけを取り出す。"""
    return [d for d in docs if d.status != "deleted" and ctx.permission(d.department_id, "draft")]


def select_docs_3(
    docs: list[models.DocumentsRow], ctx: context_types.Context
) -> list[models.DocumentsRow]:
    """用途と対象に一致するデータだけを取り出す。"""
    return [d for d in docs if d.latest_version_id and ctx.can_read(d)]


def map_versions(ctx: context_types.Context) -> dict[str, q.VersionsListRow]:
    """取得したデータを識別子別に参照できる辞書へ変換する。"""
    return {v.id: v for v in q.versions_list(ctx.db, q.VersionsListParams(organization_id=ctx.org))}


def select_docs_4(
    docs: list[models.DocumentsRow], versions: dict[str, q.VersionsListRow]
) -> list[models.DocumentsRow]:
    """用途と対象に一致するデータだけを取り出す。"""
    return [
        d.model_copy(update={"title": versions[d.latest_version_id].title})
        for d in docs
        if d.latest_version_id in versions
    ]


def select_docs_5(
    docs: list[models.DocumentsRow], status: str, search: str
) -> list[models.DocumentsRow]:
    """用途と対象に一致するデータだけを取り出す。"""
    return [
        d
        for d in docs
        if search.casefold() in d.title.casefold() and (not status or d.status == status)
    ]


def map_versions_2(ctx: context_types.Context) -> dict[str, q.VersionsListRow]:
    """取得したデータを識別子別に参照できる辞書へ変換する。"""
    return {v.id: v for v in q.versions_list(ctx.db, q.VersionsListParams(organization_id=ctx.org))}


def submissions_list(ctx: context_types.Context) -> list[q.SubmissionsListRow]:
    """現在の組織に属する承認申請を識別子順に一覧取得する。"""
    return q.submissions_list(ctx.db, q.SubmissionsListParams(organization_id=ctx.org))


def chunks_list(ctx: context_types.Context) -> list[q.ChunksListRow]:
    """現在の組織に属する検索用の文書断片を識別子順に一覧取得する。"""
    return q.chunks_list(ctx.db, q.ChunksListParams(organization_id=ctx.org))


def select_history(
    submissions: list[q.SubmissionsListRow], doc: models.DocumentsRow
) -> list[q.SubmissionsListRow]:
    """用途と対象に一致するデータだけを取り出す。"""
    return [s for s in submissions if s.document_id == doc.id]


def build_document_page(
    version: q.VersionsListRow | None,
    approval: q.SubmissionsListRow | None,
    latest: q.SubmissionsListRow | None,
    scope: str,
    versions: dict[str, q.VersionsListRow],
    chunks: list[q.ChunksListRow],
    ctx: context_types.Context,
) -> dict[str, typing.Any]:
    """後続処理に渡すデータを組み立てる。"""
    return {
        "published_number": version.number if version else None,
        "approved_at": approval.decided_at if approval else None,
        "index_ready": bool(
            version and any(c.version_id == version.id and c.ready for c in chunks)
        ),
        "summary": ctx.objects.get(version.body_key, version.body_hash).decode()[:180]
        if version and scope == "read"
        else "",
        "review_status": latest.status if latest and scope != "read" else None,
        "review_number": versions[latest.version_id].number if latest and scope != "read" else None,
    }


def build_document_page_2(
    items: list[dict[str, typing.Any]], limit: int, docs: list[models.DocumentsRow]
) -> dict[str, object]:
    """後続処理に渡すデータを組み立てる。"""
    return {"items": items, "has_next": len(docs) > limit}


def build_document_item(
    doc: models.DocumentsRow,
    versions: dict[str, q.VersionsListRow],
    submissions: list[q.SubmissionsListRow],
    chunks: list[q.ChunksListRow],
    ctx: context_types.Context,
    scope: str,
) -> dict[str, object]:
    """公開版・承認状態・索引状態・本文要約を一覧の一行へ組み立てる。"""
    version = versions.get(doc.latest_version_id or "")
    history = select_history(submissions, doc)
    latest = max(history, key=lambda s: versions[s.version_id].number, default=None)
    approval = next((s for s in history if version and s.version_id == version.id), None)
    item = doc.model_dump()
    item.update(build_document_page(version, approval, latest, scope, versions, chunks, ctx))
    return item
