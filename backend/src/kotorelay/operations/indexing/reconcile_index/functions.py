"""indexingのreconcile_indexの業務判定と処理を実行する。"""

from __future__ import annotations

import kotorelay.context as context_types
import kotorelay.operations.indexing.reconcile_index.generated.queries as q
from kotorelay.errors import require


def require_operator(ctx: context_types.Context) -> None:
    """索引整合を確認できる運用権限を確認する。"""
    return require(ctx.user.operator, "forbidden", 403)


def chunks_list(ctx: context_types.Context) -> list[q.ChunksListRow]:
    """現在の組織に属する検索用の文書断片を識別子順に一覧取得する。"""
    return q.chunks_list(ctx.db, q.ChunksListParams(organization_id=ctx.org))


def documents_list(ctx: context_types.Context) -> list[q.DocumentsListRow]:
    """現在の組織に属する文書を識別子順に一覧取得する。"""
    return q.documents_list(ctx.db, q.DocumentsListParams(organization_id=ctx.org))


def select_current(chunks: list[q.ChunksListRow], doc: q.DocumentsListRow) -> list[q.ChunksListRow]:
    """用途と対象に一致するデータだけを取り出す。"""
    return [c for c in chunks if c.document_id == doc.id]


def build_reconcile_index(doc: q.DocumentsListRow) -> dict[str, str]:
    """後続処理に渡すデータを組み立てる。"""
    return {"document_id": doc.id, "reason": "旧版または停止済みの断片が残留"}


def needs_index_repair(doc: q.DocumentsListRow, current: list[q.ChunksListRow]) -> bool:
    """有効な公開版に反映済みの断片が存在しないかを判定する。"""
    return bool(
        doc.status == "active"
        and doc.latest_version_id
        and (not any(c.version_id == doc.latest_version_id and c.ready for c in current))
    )


def build_reconcile_index_2(doc: q.DocumentsListRow) -> dict[str, str]:
    """後続処理に渡すデータを組み立てる。"""
    return {"document_id": doc.id, "reason": "最新承認版が未反映"}


def has_outdated_chunks(current: list[q.ChunksListRow], doc: q.DocumentsListRow) -> bool:
    """公開版が変わったか文書が失効したため不要になった断片があるかを判定する。"""
    return any(
        chunk.version_id != doc.latest_version_id or doc.status != "active" for chunk in current
    )
