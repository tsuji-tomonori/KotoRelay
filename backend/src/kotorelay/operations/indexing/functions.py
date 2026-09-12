"""承認と同時に保存したoutboxを再開可能に処理する。"""

from __future__ import annotations

import json

from kotorelay.context import Context, stable_id
from kotorelay.engines import Engine
from kotorelay.errors import Problem, require
from kotorelay.generated import queries as q
from kotorelay.schemas import Manifest, OcrResult


def split_chunks(body: str) -> list[tuple[str, str]]:
    chunks: list[tuple[str, str]] = []
    heading = "本文"
    buffer = ""
    for line in body.splitlines():
        if line.startswith("#") or len(buffer) + len(line) > 1200:
            if buffer.strip():
                chunks.append((heading, buffer.strip()))
            buffer = ""
            if line.startswith("#"):
                heading = line.lstrip("# ")[:200]
        for start in range(0, max(1, len(line)), 1200):
            part = line[start : start + 1200]
            if len(buffer) + len(part) > 1200 and buffer.strip():
                chunks.append((heading, buffer.strip()))
                buffer = ""
            buffer += part + "\n"
    if buffer.strip():
        chunks.append((heading, buffer.strip()))
    return chunks


def build_index(ctx: Context, job: q.OutboxRow, engine: Engine) -> str:
    doc = q.documents_get(ctx.db, ctx.org, job.document_id)[0]
    if doc.status != "active" or doc.latest_version_id != job.version_id or not job.version_id:
        return "obsolete"
    version = q.versions_get(ctx.db, ctx.org, job.version_id)[0]
    manifest = Manifest.model_validate_json(version.manifest)
    body = ctx.objects.get(version.body_key, version.body_hash).decode()
    parts: list[tuple[str, str, str]] = [
        (heading, text, "[]") for heading, text in split_chunks(body)
    ]
    for image in manifest.images:
        asset = q.assets_get(ctx.db, ctx.org, image.placement.asset_id)[0]
        run = q.ocr_runs_get(ctx.db, ctx.org, image.placement.ocr_run_id)[0]
        ctx.objects.get(asset.object_key, image.image_hash)
        result = OcrResult.model_validate_json(ctx.objects.get(run.result_key, image.ocr_hash))
        text = "\n".join(region.text for region in sorted(result.regions, key=lambda r: r.order))
        for heading, chunk in split_chunks(text or "添付画像"):
            parts.append(
                (image.placement.heading or heading, chunk, json.dumps([image.placement.id]))
            )
    require(len(parts) <= 300, "limit", 422)
    previous = {c.id: c for c in q.chunks_list(ctx.db, ctx.org) if c.version_id == version.id}
    for number, (heading, text, placements) in enumerate(parts):
        key = ctx.objects.put(text.encode(), "text/plain")
        chunk = q.ChunksRow(
            id=stable_id(version.id + str(number)),
            organization_id=ctx.org,
            document_id=doc.id,
            version_id=version.id,
            body_key=key,
            sha256=key,
            heading=heading,
            placements=placements,
            manifest_hash=version.manifest_hash,
            ready=True,
        )
        engine.index(chunk.id, text, doc.id, version.id)
        if chunk.id in previous:
            q.chunks_update(ctx.db, chunk)
        else:
            q.chunks_insert(ctx.db, chunk)
    actual = [c for c in q.chunks_list(ctx.db, ctx.org) if c.version_id == version.id]
    require(len(actual) == len(parts) and all(c.ready for c in actual), "integrity", 503)
    return "done"


def purge(ctx: Context, job: q.OutboxRow, engine: Engine) -> str:
    doc = q.documents_get(ctx.db, ctx.org, job.document_id)[0]
    if doc.status != "deleted":
        return "obsolete"
    chunks = [c for c in q.chunks_list(ctx.db, ctx.org) if c.document_id == doc.id]
    engine.delete([c.id for c in chunks])
    for chunk in chunks[:100]:
        q.chunks_delete(ctx.db, ctx.org, chunk.id)
    if len(chunks) > 100:
        return "pending"
    runs = [r for r in q.ocr_runs_list(ctx.db, ctx.org) if r.document_id == doc.id]
    for run in runs[:100]:
        q.ocr_runs_delete(ctx.db, ctx.org, run.id)
    if len(runs) > 100:
        return "pending"
    for asset in q.assets_list(ctx.db, ctx.org):
        if asset.document_id == doc.id:
            q.assets_delete(ctx.db, ctx.org, asset.id)
    for draft in q.drafts_list(ctx.db, ctx.org):
        if draft.document_id == doc.id:
            q.drafts_delete(ctx.db, ctx.org, draft.id)
    # 監査と承認版の参照を保持する。実体のGCは保持期限後に別処理で行う。
    return "retained"


def process(ctx: Context, engine: Engine, job_id: str) -> q.OutboxRow:
    require(ctx.user.operator, "forbidden", 403)
    rows = q.outbox_get(ctx.db, ctx.org, job_id)
    require(bool(rows))
    job = rows[0]
    require(job.attempts < 5, "limit", 429)
    if job.status in {"done", "obsolete", "retained"}:
        return job
    try:
        status = purge(ctx, job, engine) if job.kind == "purge" else build_index(ctx, job, engine)
        updated = job.model_copy(
            update={"status": status, "attempts": job.attempts + 1, "error_code": ""}
        )
    except Problem as exc:
        updated = job.model_copy(
            update={"status": "failed", "attempts": job.attempts + 1, "error_code": exc.code}
        )
    q.outbox_update(ctx.db, updated)
    ctx.fence()
    return updated


def jobs(ctx: Context) -> list[q.OutboxRow]:
    require(ctx.user.operator, "forbidden", 403)
    return q.outbox_list(ctx.db, ctx.org)


def reconcile(ctx: Context) -> list[dict[str, str]]:
    require(ctx.user.operator, "forbidden", 403)
    chunks = q.chunks_list(ctx.db, ctx.org)
    differences: list[dict[str, str]] = []
    for doc in q.documents_list(ctx.db, ctx.org):
        current = [c for c in chunks if c.document_id == doc.id]
        if any(c.version_id != doc.latest_version_id or doc.status != "active" for c in current):
            differences.append({"document_id": doc.id, "reason": "旧版または停止済みの断片が残留"})
        if (
            doc.status == "active"
            and doc.latest_version_id
            and not any(c.version_id == doc.latest_version_id and c.ready for c in current)
        ):
            differences.append({"document_id": doc.id, "reason": "最新承認版が未反映"})
    return differences
