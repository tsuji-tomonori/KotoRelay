"""documentsのread_documentの業務判定と処理を実行する。"""

from __future__ import annotations

import uuid

import kotorelay.context as context_types
import kotorelay.generated.models as models
import kotorelay.operations.documents.read_document.generated.queries as q
from kotorelay.errors import require


def documents_get(ctx: context_types.Context, document_id: uuid.UUID) -> list[q.DocumentsGetRow]:
    """現在の組織に属する指定の文書について、文書の所有部署・公開範囲・状態・公開版の参照を取得する。"""
    return q.documents_get(
        ctx.db, q.DocumentsGetParams(organization_id=ctx.org, id=str(document_id))
    )


def require_document(rows: list[q.DocumentsGetRow]) -> None:
    """文書が存在することを確認する。"""
    return require(bool(rows))


def require_retained_document(doc: q.DocumentsGetRow) -> None:
    """文書が削除状態でないことを確認する。"""
    return require(doc.status != "deleted")


def require_read_permission(doc: q.DocumentsGetRow, ctx: context_types.Context) -> None:
    """公開版の閲覧権限または下書きの閲覧権限を確認する。"""
    return require(ctx.can_read(doc) or ctx.permission(doc.department_id, "draft"))


def require_selected_version(chosen: str | None) -> None:
    """表示する確定版が指定または公開されていることを確認する。"""
    return require(chosen is not None)


def version_version(
    doc: q.DocumentsGetRow, ctx: context_types.Context, chosen: str | None
) -> models.VersionsRow:
    """対象文書に属する確定版を取得する。"""
    return ctx.version(doc, str(chosen))


def build_read_document(
    version: models.VersionsRow, doc: q.DocumentsGetRow, ctx: context_types.Context
) -> dict[str, object]:
    """後続処理に渡すデータを組み立てる。"""
    return {
        "document": doc.model_copy(update={"title": version.title}),
        "version": version,
        "body": ctx.objects.get(version.body_key, version.body_hash).decode(),
        "index_ready": any(
            c.version_id == version.id and c.ready
            for c in q.chunks_list(ctx.db, q.ChunksListParams(organization_id=ctx.org))
        ),
    }


def has_requested_version(version_id: object | None) -> bool:
    """表示する版が指定されている。"""
    return bool(version_id)
