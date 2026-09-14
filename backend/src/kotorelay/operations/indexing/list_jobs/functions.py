"""indexingのlist_jobsの業務判定と処理を実行する。"""

from __future__ import annotations

import kotorelay.context as context_types
import kotorelay.generated.models as models
import kotorelay.operations.indexing.list_jobs.generated.queries as q
from kotorelay.errors import require


def select_list_jobs(rows: list[models.OutboxRow]) -> list[dict[str, object]]:
    """用途と対象に一致するデータだけを取り出す。"""
    return [row.model_dump() for row in rows]


def require_operator(ctx: context_types.Context) -> None:
    """索引ジョブを閲覧できる運用権限を確認する。"""
    return require(ctx.user.operator, "forbidden", 403)


def outbox_list(ctx: context_types.Context) -> list[q.OutboxListRow]:
    """現在の組織に属する反映・削除ジョブを識別子順に一覧取得する。"""
    return q.outbox_list(ctx.db, q.OutboxListParams(organization_id=ctx.org))


def map_docs(ctx: context_types.Context) -> dict[str, q.DocumentsListRow]:
    """取得したデータを識別子別に参照できる辞書へ変換する。"""
    return {
        d.id: d for d in q.documents_list(ctx.db, q.DocumentsListParams(organization_id=ctx.org))
    }


def map_versions(ctx: context_types.Context) -> dict[str, q.VersionsListRow]:
    """取得したデータを識別子別に参照できる辞書へ変換する。"""
    return {v.id: v for v in q.versions_list(ctx.db, q.VersionsListParams(organization_id=ctx.org))}


def select_job_details(
    rows: list[models.OutboxRow],
    docs: dict[str, q.DocumentsListRow],
    versions: dict[str, q.VersionsListRow],
) -> list[dict[str, object]]:
    """用途と対象に一致するデータだけを取り出す。"""
    return [
        dict(
            row.model_dump(),
            title=docs[row.document_id].title,
            version_number=versions[row.version_id].number if row.version_id else None,
        )
        for row in rows
    ]


def requests_details(details: bool) -> bool:
    """ジョブに文書名と版番号を含めるよう要求されている。"""
    return details
