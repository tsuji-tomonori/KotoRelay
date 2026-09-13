"""list_documentsのHTTP入力と業務処理の順序を宣言する。"""

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
    department = str(department_id) if department_id else None
    if page:
        return build_response(
            f.document_page(ctx, scope, offset, limit, search, department, status)
        )
    return build_response(f.list_documents(ctx, scope, offset, limit, search, department, status))
