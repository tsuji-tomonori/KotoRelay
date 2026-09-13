"""list_documentsのHTTP入力と業務処理の順序を宣言する。"""

from __future__ import annotations

from typing import Annotated, Literal
from uuid import UUID

from fastapi import APIRouter, Query

from kotorelay.context import Context
from kotorelay.generated import models
from kotorelay.operations.documents.list_documents import functions as f
from kotorelay.operations.documents.list_documents.contract import CONTRACT
from kotorelay.operations.documents.list_documents.response_builders import build_response
from kotorelay.operations.documents.list_documents.samples import SAMPLES
from kotorelay.runtime import Ctx

router = APIRouter(prefix="/api/documents", tags=["文書"])


@router.get(
    "",
    summary="閲覧可能な文書を検索",
    operation_id="list_documents",
    openapi_extra=CONTRACT.openapi_extra(SAMPLES),
)
def list_documents(
    ctx: Ctx,
    scope: Literal["read", "work", "manage"] = "read",
    offset: Annotated[int, Query(ge=0)] = 0,
    limit: Annotated[int, Query(ge=1, le=100)] = 30,
    search: Annotated[str, Query(max_length=200)] = "",
    department_id: UUID | None = None,
    status: Literal["", "active", "withdrawn", "deleted"] = "",
    page: bool = False,
) -> list[models.DocumentsRow] | dict[str, object]:
    department = str(department_id) if department_id else None
    if page:
        return build_response(document_page(ctx, scope, offset, limit, search, department, status))
    return build_response(_select_documents(ctx, scope, offset, limit, search, department, status))


def _select_documents(
    ctx: Context,
    scope: str,
    offset: int,
    limit: int,
    search: str,
    department_id: str | None = None,
    status: str = "",
) -> list[models.DocumentsRow]:
    if department_id and f.requires_department_permission(department_id, scope):
        f.require_department_permission(department_id, ctx, scope)
    docs: list[models.DocumentsRow] = list(
        f.documents_by_department(ctx, department_id) if department_id else f.documents_list(ctx)
    )
    if f.is_management_scope(scope):
        docs = f.select_docs(docs, ctx)
    elif f.is_authoring_scope(scope):
        docs = f.select_docs_2(docs, ctx)
    else:
        docs = f.select_docs_3(docs, ctx)
        versions = f.map_versions(ctx)
        docs = f.select_docs_4(docs, versions)
    docs = f.select_docs_5(docs, status, search)
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
    docs = _select_documents(ctx, scope, offset, limit + 1, search, department_id, status)
    versions = f.map_versions_2(ctx)
    submissions = f.submissions_list(ctx)
    chunks = f.chunks_list(ctx)
    items = []
    for doc in docs[:limit]:
        items.append(f.build_document_item(doc, versions, submissions, chunks, ctx, scope))
    return f.build_document_page_2(items, limit, docs)
