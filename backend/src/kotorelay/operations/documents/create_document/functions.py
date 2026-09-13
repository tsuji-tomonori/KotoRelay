"""documentsのcreate_documentの業務判定と処理を実行する。"""

from __future__ import annotations

from kotorelay.context import Context, new_id, now
from kotorelay.errors import require
from kotorelay.generated import models
from kotorelay.operations.documents.create_document.generated import queries as q
from kotorelay.operations.documents.create_document.schemas import CreateDocument


def create(ctx: Context, data: CreateDocument) -> models.DocumentsRow:
    require(ctx.permission(data.department_id, "author"), "forbidden", 403)
    doc = models.DocumentsRow(
        id=new_id(),
        organization_id=ctx.org,
        department_id=data.department_id,
        title=data.title,
        created_by=ctx.user.id,
        visibility="department",
        shared_departments="[]",
        status="active",
        revision=1,
        next_version=1,
        latest_version_id=None,
        updated_at=now(),
    )
    q.documents_insert(ctx.db, doc)
    key = ctx.objects.put(b"")
    q.drafts_insert(
        ctx.db,
        models.DraftsRow(
            id=new_id(),
            organization_id=ctx.org,
            document_id=doc.id,
            body_key=key,
            body_hash=key,
            placements="[]",
            revision=1,
            updated_by=ctx.user.id,
        ),
    )
    ctx.audit("create", doc.id)
    ctx.fence()
    return doc
