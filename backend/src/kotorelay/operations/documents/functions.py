"""文書の下書き、変更不能な版、公開範囲と履歴を管理する。"""

from __future__ import annotations

import difflib
import json

from kotorelay.context import Context, new_id, now
from kotorelay.errors import require
from kotorelay.generated import queries as q
from kotorelay.objects import digest
from kotorelay.schemas import (
    ChangePolicy,
    CreateDocument,
    Manifest,
    ManifestImage,
    Placement,
    SaveDraft,
    Submit,
)


def create(ctx: Context, data: CreateDocument) -> q.DocumentsRow:
    require(ctx.permission(data.department_id, "author"), "forbidden", 403)
    doc = q.DocumentsRow(
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
        q.DraftsRow(
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


def list_documents(
    ctx: Context, scope: str, offset: int, limit: int, search: str
) -> list[q.DocumentsRow]:
    docs = q.documents_list(ctx.db, ctx.org)
    if scope == "manage":
        docs = [d for d in docs if ctx.permission(d.department_id, "manage")]
    elif scope == "work":
        docs = [
            d for d in docs if d.status != "deleted" and ctx.permission(d.department_id, "draft")
        ]
    else:
        docs = [d for d in docs if d.latest_version_id and ctx.can_read(d)]
        versions = {v.id: v for v in q.versions_list(ctx.db, ctx.org)}
        docs = [
            d.model_copy(update={"title": versions[d.latest_version_id].title})
            for d in docs
            if d.latest_version_id in versions
        ]
    docs = [d for d in docs if search.casefold() in d.title.casefold()]
    return sorted(docs, key=lambda d: d.updated_at, reverse=True)[offset : offset + limit]


def draft(ctx: Context, document_id: str) -> dict[str, object]:
    doc = ctx.document(document_id, "draft")
    row = next(d for d in q.drafts_list(ctx.db, ctx.org) if d.document_id == doc.id)
    return {
        "document": doc,
        "body": ctx.objects.get(row.body_key, row.body_hash).decode(),
        "revision": row.revision,
        "placements": json.loads(row.placements),
    }


def validate_placements(ctx: Context, doc: q.DocumentsRow, data: SaveDraft) -> None:
    require(len({p.id for p in data.placements}) == len(data.placements), "invalid_placement", 422)
    for placement in data.placements:
        assets = q.assets_get(ctx.db, ctx.org, placement.asset_id)
        runs = q.ocr_runs_get(ctx.db, ctx.org, placement.ocr_run_id)
        require(bool(assets) and bool(runs), "invalid_placement", 422)
        require(
            assets[0].document_id == doc.id
            and runs[0].asset_id == assets[0].id
            and runs[0].document_id == doc.id
            and placement.offset <= len(data.body),
            "invalid_placement",
            422,
        )


def save(ctx: Context, document_id: str, data: SaveDraft) -> dict[str, object]:
    doc = ctx.document(document_id, "author")
    row = next(d for d in q.drafts_list(ctx.db, ctx.org) if d.document_id == doc.id)
    require(row.revision == data.revision, "conflict", 409)
    validate_placements(ctx, doc, data)
    key = ctx.objects.put(data.body.encode(), "text/markdown")
    q.drafts_update(
        ctx.db,
        row.model_copy(
            update={
                "body_key": key,
                "body_hash": key,
                "revision": row.revision + 1,
                "updated_by": ctx.user.id,
                "placements": json.dumps([p.model_dump() for p in data.placements]),
            }
        ),
    )
    q.documents_update(
        ctx.db,
        doc.model_copy(
            update={"title": data.title, "revision": doc.revision + 1, "updated_at": now()}
        ),
    )
    ctx.fence()
    return draft(ctx, doc.id)


def submit(ctx: Context, document_id: str, data: Submit, key: str) -> q.VersionsRow:
    doc = ctx.document(document_id, "author")
    request = document_id + data.model_dump_json()
    cached = ctx.idempotent_result(key, "submit", request)
    if cached:
        return q.VersionsRow.model_validate_json(cached)
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
    version = q.VersionsRow(
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
        q.SubmissionsRow(
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


def read_version(ctx: Context, document_id: str, version_id: str | None) -> dict[str, object]:
    rows = q.documents_get(ctx.db, ctx.org, document_id)
    require(bool(rows))
    doc = rows[0]
    require(doc.status != "deleted")
    require(ctx.can_read(doc) or ctx.permission(doc.department_id, "draft"))
    chosen = version_id or doc.latest_version_id
    require(chosen is not None)
    version = ctx.version(doc, str(chosen))
    return {
        "document": doc.model_copy(update={"title": version.title}),
        "version": version,
        "body": ctx.objects.get(version.body_key, version.body_hash).decode(),
        "index_ready": any(
            c.version_id == version.id and c.ready for c in q.chunks_list(ctx.db, ctx.org)
        ),
    }


def history(ctx: Context, document_id: str) -> list[dict[str, object]]:
    doc = ctx.document(document_id, "draft")
    submissions = {s.version_id: s for s in q.submissions_list(ctx.db, ctx.org)}
    return [
        {"version": v, "submission": submissions.get(v.id)}
        for v in sorted(q.versions_list(ctx.db, ctx.org), key=lambda v: v.number, reverse=True)
        if v.document_id == doc.id
    ]


def diff(ctx: Context, document_id: str, left: str, right: str) -> dict[str, str]:
    doc = ctx.document(document_id, "draft")
    a, b = ctx.version(doc, left), ctx.version(doc, right)
    lines = difflib.unified_diff(
        ctx.objects.get(a.body_key).decode().splitlines(),
        ctx.objects.get(b.body_key).decode().splitlines(),
        fromfile=left,
        tofile=right,
        lineterm="",
    )
    return {"left": left, "right": right, "diff": "\n".join(lines)}


def policy(ctx: Context, document_id: str, data: ChangePolicy) -> q.DocumentsRow:
    doc = ctx.document(document_id, "manage")
    require(doc.revision == data.revision, "conflict", 409)
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
        q.OutboxRow(
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
    ctx.audit("policy", doc.id, before=doc.status, after=data.status)
    ctx.fence()
    return updated
