"""承認と同時に保存したoutboxを再開可能に処理する。"""

from __future__ import annotations

import json

from botocore.exceptions import BotoCoreError, ClientError

from kotorelay.context import Context, now, stable_id
from kotorelay.engines import Engine
from kotorelay.errors import Problem, require
from kotorelay.generated import queries as q
from kotorelay.schemas import Evidence, Manifest, OcrResult


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
    if doc.latest_version_id != job.version_id or not job.version_id:
        return "obsolete"
    stale = [
        c
        for c in q.chunks_list(ctx.db, ctx.org)
        if c.document_id == doc.id and (doc.status != "active" or c.version_id != job.version_id)
    ]
    engine.delete([c.id for c in stale[:100]])
    for chunk in stale[:100]:
        q.chunks_delete(ctx.db, ctx.org, chunk.id)
    if len(stale) > 100:
        return "pending"
    if doc.status != "active":
        return "done"
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
        for heading, image_text in split_chunks(text or "添付画像"):
            parts.append(
                (image.placement.heading or heading, image_text, json.dumps([image.placement.id]))
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
            ready=False,
        )
        engine.index(chunk.id, text, doc.id, version.id)
        if chunk.id in previous:
            q.chunks_update(ctx.db, chunk)
        else:
            q.chunks_insert(ctx.db, chunk)
    actual = [c for c in q.chunks_list(ctx.db, ctx.org) if c.version_id == version.id]
    require(len(actual) == len(parts) and engine.verify([c.id for c in actual]), "integrity", 503)
    for current in actual:
        ctx.objects.get(current.body_key, current.sha256)
        q.chunks_update(ctx.db, current.model_copy(update={"ready": True}))
    return "done"


def purge(ctx: Context, job: q.OutboxRow, engine: Engine) -> str:
    doc = q.documents_get(ctx.db, ctx.org, job.document_id)[0]
    if doc.status != "deleted":
        return "obsolete"
    if (now() - job.created_at).total_seconds() < ctx.settings.retention_days * 86400:
        return "retained"
    chunks = q.chunks_list(ctx.db, ctx.org)
    assets = q.assets_list(ctx.db, ctx.org)
    runs = q.ocr_runs_list(ctx.db, ctx.org)
    drafts = q.drafts_list(ctx.db, ctx.org)
    versions = q.versions_list(ctx.db, ctx.org)
    answers = q.answers_list(ctx.db, ctx.org)
    keys: set[str] = set()
    protected: set[str] = set()
    live = {d.id for d in q.documents_list(ctx.db, ctx.org) if d.status != "deleted"}
    sources: list[
        tuple[
            list[q.ChunksRow]
            | list[q.AssetsRow]
            | list[q.OcrRunsRow]
            | list[q.DraftsRow]
            | list[q.VersionsRow],
            str,
        ]
    ] = [
        (chunks, "body_key"),
        (assets, "object_key"),
        (runs, "result_key"),
        (drafts, "body_key"),
        (versions, "body_key"),
    ]
    for rows, column in sources:
        for row in rows:
            if row.document_id == doc.id:
                keys.add(str(getattr(row, column)))
            elif row.document_id in live:
                protected.add(str(getattr(row, column)))
    for answer in answers:
        evidence = Evidence.model_validate_json(answer.evidence)
        target = keys if any(c.document_id == doc.id for c in evidence.citations) else protected
        target.add(answer.answer_key)
        protected.add(answer.question_key)
    # 共有された内容ハッシュは他文書の実体を残す。監査用の版メタデータは保持する。
    for key in sorted(keys - protected):
        ctx.objects.delete(key)
    target_chunks = [c for c in chunks if c.document_id == doc.id]
    engine.delete([c.id for c in target_chunks])
    for chunk in target_chunks[:100]:
        q.chunks_delete(ctx.db, ctx.org, chunk.id)
    if len(target_chunks) > 100:
        return "pending"
    target_runs = [r for r in runs if r.document_id == doc.id]
    for run in target_runs[:100]:
        q.ocr_runs_delete(ctx.db, ctx.org, run.id)
    if len(target_runs) > 100:
        return "pending"
    for asset in assets:
        if asset.document_id == doc.id:
            q.assets_delete(ctx.db, ctx.org, asset.id)
    for draft in drafts:
        if draft.document_id == doc.id:
            q.drafts_delete(ctx.db, ctx.org, draft.id)
    return "done"


def process(ctx: Context, engine: Engine, job_id: str) -> q.OutboxRow:
    require(ctx.user.operator, "forbidden", 403)
    rows = q.outbox_get(ctx.db, ctx.org, job_id)
    require(bool(rows))
    job = rows[0]
    require(job.attempts < 5, "limit", 429)
    if job.status in {"done", "obsolete"}:
        return job
    try:
        status = purge(ctx, job, engine) if job.kind == "purge" else build_index(ctx, job, engine)
        updated = job.model_copy(
            update={
                "status": status,
                "attempts": job.attempts if status in {"retained", "pending"} else job.attempts + 1,
                "error_code": "",
            }
        )
    except Problem as exc:
        updated = job.model_copy(
            update={"status": "failed", "attempts": job.attempts + 1, "error_code": exc.code}
        )
    except (OSError, BotoCoreError, ClientError):
        updated = job.model_copy(
            update={
                "status": "failed",
                "attempts": job.attempts + 1,
                "error_code": "external_failure",
            }
        )
    q.outbox_update(ctx.db, updated)
    ctx.fence()
    return updated


def jobs(ctx: Context) -> list[q.OutboxRow]:
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
