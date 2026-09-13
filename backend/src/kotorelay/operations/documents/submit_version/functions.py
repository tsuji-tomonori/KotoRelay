"""documentsのsubmit_versionの業務判定と処理を実行する。"""

from __future__ import annotations

import json

from kotorelay.context import Context, new_id, now
from kotorelay.errors import require
from kotorelay.generated import models
from kotorelay.objects import digest
from kotorelay.operations.documents.submit_version.generated import queries as q
from kotorelay.operations.documents.submit_version.schemas import Submit
from kotorelay.schemas import Manifest, ManifestImage, Placement


def submit(ctx: Context, document_id: str, data: Submit, key: str) -> models.VersionsRow:
    doc = ctx.document(document_id, "author")
    request = document_id + data.model_dump_json()
    cached = ctx.idempotent_result(key, "submit", request)
    if cached:
        return models.VersionsRow.model_validate_json(cached)
    row = next(d for d in q.drafts_list(ctx.db, ctx.org) if d.document_id == doc.id)
    require(row.revision == data.revision, "conflict", 409)
    images: list[ManifestImage] = []
    for value in json.loads(row.placements):
        placement = Placement.model_validate(value)
        asset = q.assets_get(ctx.db, ctx.org, placement.asset_id)[0]
        ocr = q.ocr_runs_get(ctx.db, ctx.org, placement.ocr_run_id)[0]
        require(ocr.confirmed and ocr.status == "ready", "ocr_unconfirmed", 409)
        ctx.objects.get(asset.object_key, asset.sha256)
        ctx.objects.get(ocr.result_key, ocr.result_hash)
        images.append(
            ManifestImage(placement=placement, image_hash=asset.sha256, ocr_hash=ocr.result_hash)
        )
    ctx.objects.get(row.body_key, row.body_hash)
    manifest = Manifest(body_hash=row.body_hash, images=images).model_dump_json()
    version = models.VersionsRow(
        id=new_id(),
        organization_id=ctx.org,
        document_id=doc.id,
        number=doc.next_version,
        title=doc.title,
        body_key=row.body_key,
        body_hash=row.body_hash,
        manifest=manifest,
        manifest_hash=digest(manifest.encode()),
        created_by=ctx.user.id,
        created_at=now(),
    )
    q.versions_insert(ctx.db, version)
    q.submissions_insert(
        ctx.db,
        models.SubmissionsRow(
            id=new_id(),
            organization_id=ctx.org,
            document_id=doc.id,
            version_id=version.id,
            requested_by=ctx.user.id,
            status="pending",
            manifest_hash=version.manifest_hash,
            decided_by=None,
            reason="",
            created_at=now(),
            decided_at=None,
        ),
    )
    q.documents_update(
        ctx.db,
        doc.model_copy(
            update={
                "next_version": doc.next_version + 1,
                "revision": doc.revision + 1,
                "updated_at": now(),
            }
        ),
    )
    ctx.audit("submit", doc.id, version.id, "draft", "pending")
    ctx.remember(key, "submit", request, version.model_dump_json())
    ctx.fence()
    return version
