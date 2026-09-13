"""indexingのlist_jobsの業務判定と処理を実行する。"""

from __future__ import annotations

from kotorelay.context import Context
from kotorelay.errors import require
from kotorelay.generated import models
from kotorelay.operations.indexing.list_jobs.generated import queries as q


def jobs(ctx: Context) -> list[models.OutboxRow]:
    require(ctx.user.operator, "forbidden", 403)
    return q.outbox_list(ctx.db, ctx.org)


def job_details(ctx: Context) -> list[dict[str, object]]:
    rows = jobs(ctx)
    docs = {d.id: d for d in q.documents_list(ctx.db, ctx.org)}
    versions = {v.id: v for v in q.versions_list(ctx.db, ctx.org)}
    return [
        dict(
            row.model_dump(),
            title=docs[row.document_id].title,
            version_number=versions[row.version_id].number if row.version_id else None,
        )
        for row in rows
    ]


def list_jobs(ctx: Context, details: bool) -> list[dict[str, object]]:
    """要求された詳細度に合わせて運用者向けジョブ一覧を取得する。"""
    if details:
        return job_details(ctx)
    return [row.model_dump() for row in jobs(ctx)]
