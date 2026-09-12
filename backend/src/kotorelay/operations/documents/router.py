"""文書APIの入力と業務関数を対応付ける。"""

from typing import Annotated, Literal
from uuid import UUID

from fastapi import APIRouter, Header, Query

from kotorelay.generated import queries as q
from kotorelay.operations.documents import functions as f
from kotorelay.runtime import Ctx
from kotorelay.schemas import ChangePolicy, CreateDocument, SaveDraft, Submit

router = APIRouter(prefix="/api/documents", tags=["文書"])
Key = Annotated[UUID, Header(alias="Idempotency-Key")]


@router.get("", summary="閲覧可能な文書を検索", operation_id="list_documents")
def list_documents(
    ctx: Ctx,
    scope: Literal["read", "work", "manage"] = "read",
    offset: Annotated[int, Query(ge=0)] = 0,
    limit: Annotated[int, Query(ge=1, le=100)] = 30,
    search: Annotated[str, Query(max_length=200)] = "",
    department_id: UUID | None = None,
    status: Literal["", "active", "withdrawn", "deleted"] = "",
    page: bool = False,
) -> list[q.DocumentsRow] | dict[str, object]:
    department = str(department_id) if department_id else None
    if page:
        return f.document_page(ctx, scope, offset, limit, search, department, status)
    return f.list_documents(ctx, scope, offset, limit, search, department, status)


@router.post("", status_code=201, summary="文書を作成", operation_id="create_document")
def create_document(ctx: Ctx, data: CreateDocument) -> q.DocumentsRow:
    return f.create(ctx, data)


@router.get("/{document_id}/draft", summary="下書きを取得", operation_id="get_draft")
def get_draft(ctx: Ctx, document_id: UUID) -> dict[str, object]:
    return f.draft(ctx, str(document_id))


@router.put("/{document_id}/draft", summary="競合を検出して下書きを保存", operation_id="save_draft")
def save_draft(ctx: Ctx, document_id: UUID, data: SaveDraft) -> dict[str, object]:
    return f.save(ctx, str(document_id), data)


@router.post(
    "/{document_id}/submissions",
    status_code=201,
    summary="版を確定して承認申請",
    operation_id="submit_version",
)
def submit_version(ctx: Ctx, document_id: UUID, data: Submit, key: Key) -> q.VersionsRow:
    return f.submit(ctx, str(document_id), data, str(key))


@router.get("/{document_id}", summary="承認版または担当版を表示", operation_id="read_document")
def read_document(ctx: Ctx, document_id: UUID, version_id: UUID | None = None) -> dict[str, object]:
    return f.read_version(ctx, str(document_id), str(version_id) if version_id else None)


@router.get("/{document_id}/history", summary="担当文書の版履歴", operation_id="version_history")
def version_history(ctx: Ctx, document_id: UUID) -> list[dict[str, object]]:
    return f.history(ctx, str(document_id))


@router.get(
    "/{document_id}/diff", summary="版IDを指定して本文差分を比較", operation_id="version_diff"
)
def version_diff(ctx: Ctx, document_id: UUID, left: UUID, right: UUID) -> dict[str, str]:
    return f.diff(ctx, str(document_id), str(left), str(right))


@router.put(
    "/{document_id}/policy",
    summary="リーダーが公開範囲・公開停止・削除を管理",
    operation_id="change_policy",
)
def change_policy(ctx: Ctx, document_id: UUID, data: ChangePolicy) -> q.DocumentsRow:
    return f.policy(ctx, str(document_id), data)
