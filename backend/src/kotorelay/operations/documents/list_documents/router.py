"""list_documentsのHTTP入力と業務処理の順序を宣言する。"""

from __future__ import annotations

from typing import Annotated, Literal
from uuid import UUID

from fastapi import APIRouter, Query

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
    """閲覧権限で文書を絞り込み、要求時だけページ用の付加情報を返す。"""
    department = str(department_id) if department_id else None
    if department and f.requires_department_permission(department, scope):
        f.require_department_permission(department, ctx, scope)
    docs: list[models.DocumentsRow] = list(
        f.documents_by_department(ctx, department) if department else f.documents_list(ctx)
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
    docs = f.paginate_documents(docs, offset, limit + 1 if page else limit)
    if not page:
        return build_response(docs)
    versions = f.map_versions_2(ctx)
    submissions = f.submissions_list(ctx)
    chunks = f.chunks_list(ctx)
    items = []
    for doc in docs[:limit]:
        items.append(f.build_document_item(doc, versions, submissions, chunks, ctx, scope))
    return build_response(f.build_document_page_2(items, limit, docs))
