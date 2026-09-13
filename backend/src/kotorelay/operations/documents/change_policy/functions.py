"""documentsのchange_policyの業務判定と処理を実行する。"""

from __future__ import annotations

import json

from kotorelay.context import Context, new_id, now
from kotorelay.errors import require
from kotorelay.generated import models
from kotorelay.operations.documents.change_policy.generated import queries as q
from kotorelay.operations.documents.change_policy.schemas import ChangePolicy


def policy(ctx: Context, document_id: str, data: ChangePolicy) -> models.DocumentsRow:
    doc = ctx.document(document_id, "manage")
    require(doc.revision == data.revision, "conflict", 409)
    require(data.status != "deleted" or bool(data.reason.strip()), "reason_required", 422)
    departments = {d.id for d in q.departments_list(ctx.db, ctx.org) if d.active}
    require(set(data.shared_departments) <= departments, "forbidden", 422)
    updated = doc.model_copy(
        update={
            "visibility": data.visibility,
            "shared_departments": json.dumps(data.shared_departments),
            "status": data.status,
            "revision": doc.revision + 1,
            "updated_at": now(),
        }
    )
    q.documents_update(ctx.db, updated)
    q.outbox_insert(
        ctx.db,
        models.OutboxRow(
            id=new_id(),
            organization_id=ctx.org,
            document_id=doc.id,
            version_id=doc.latest_version_id,
            kind="purge" if data.status == "deleted" else "index",
            status="pending",
            attempts=0,
            error_code="",
            created_at=now(),
        ),
    )
    ctx.audit("policy", doc.id, before=doc.status, after=data.status, reason=data.reason)
    ctx.fence()
    return updated
