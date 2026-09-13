"""documentsのversion_historyの業務判定と処理を実行する。"""

from __future__ import annotations

import uuid

import kotorelay.context as context_types
import kotorelay.generated.models as models
import kotorelay.operations.documents.version_history.generated.queries as q


def document_doc(ctx: context_types.Context, document_id: uuid.UUID) -> models.DocumentsRow:
    """文書を取得して要求された操作の権限を確認する。"""
    return ctx.document(str(document_id), "draft")


def map_submissions(ctx: context_types.Context) -> dict[str, q.SubmissionsListRow]:
    """取得したデータを識別子別に参照できる辞書へ変換する。"""
    return {
        s.version_id: s
        for s in q.submissions_list(ctx.db, q.SubmissionsListParams(organization_id=ctx.org))
    }


def select_version_history(
    submissions: dict[str, q.SubmissionsListRow],
    doc: models.DocumentsRow,
    ctx: context_types.Context,
) -> list[dict[str, object]]:
    """用途と対象に一致するデータだけを取り出す。"""
    return [
        {"version": v, "submission": submissions.get(v.id)}
        for v in sorted(
            q.versions_list(ctx.db, q.VersionsListParams(organization_id=ctx.org)),
            key=lambda v: v.number,
            reverse=True,
        )
        if v.document_id == doc.id
    ]
