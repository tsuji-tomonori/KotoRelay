"""APIとworkerが共有する索引配送の順序・分岐・例外を管理する。"""

from __future__ import annotations

from typing import cast

from botocore.exceptions import BotoCoreError, ClientError

from kotorelay.context import Context
from kotorelay.engines import Engine
from kotorelay.errors import Problem
from kotorelay.generated import models
from kotorelay.operational_logging import MessageId, continuation_context, ops_logger
from kotorelay.operations.indexing.shared import functions as f


def build_index(ctx: Context, job: models.OutboxRow, engine: Engine) -> str:
    """現行版の索引を分割更新し、外部実体の検証後に反映済みへ進める。"""
    doc = f.documents_get(ctx, job)[0]
    if f.is_obsolete_version(doc, job):
        return "obsolete"
    stale = f.select_stale(ctx, doc, job)
    f.delete_build_index(engine, stale)
    for stale_chunk in stale[:100]:
        f.chunks_delete(ctx, stale_chunk)
    if f.has_more_stale_chunks(stale):
        return "pending"
    if f.is_inactive_document(doc):
        return "done"
    version = f.versions_get(ctx, cast(str, job.version_id))[0]
    manifest = f.build_manifest(version)
    body = f.decode_body(version, ctx)
    parts: list[tuple[str, str, str]] = f.select_parts(body)
    for image in manifest.images:
        asset = f.assets_get(ctx, image)[0]
        run = f.ocr_runs_get(ctx, image)[0]
        f.verify_image_object(asset, image, ctx)
        result = f.build_result(run, image, ctx)
        parts.extend(f.image_chunks(result, image))
    f.enforce_chunk_limit(parts)
    previous = f.map_previous(ctx, version)
    for number, (heading, text, placements) in enumerate(parts):
        key = f.put_key(ctx, text)
        chunk = f.build_chunk(key, heading, placements, ctx, doc, version, number)
        f.index_build_index(text, engine, chunk, doc, version)
        if f.is_existing_chunk(previous, chunk):
            f.chunks_update(ctx, chunk)
        else:
            f.chunks_insert(ctx, chunk)
    actual = f.select_actual(ctx, version)
    f.verify_index_completion(actual, parts, engine)
    for current in actual:
        f.verify_chunk_object(current, ctx)
        f.chunks_update_2(ctx, current)
    return "done"


def purge(ctx: Context, job: models.OutboxRow, engine: Engine) -> str:
    """保持期間と共有実体を確認し、削除対象の索引と画像を段階的に除去する。"""
    doc = f.documents_get_2(ctx, job)[0]
    if f.is_restored_document(doc):
        return "obsolete"
    if f.is_within_retention(ctx, job):
        return "retained"
    chunks = f.chunks_list(ctx)
    assets = f.assets_list(ctx)
    runs = f.ocr_runs_list(ctx)
    drafts = f.drafts_list(ctx)
    versions = f.versions_list(ctx)
    answers = f.answers_list(ctx)
    live = f.collect_live(ctx)
    keys, protected = f.collect_object_keys(
        doc.id, live, chunks, assets, runs, drafts, versions, answers
    )
    for key in sorted(keys - protected):
        f.delete_purge(key, ctx)
    target_chunks = f.select_target_chunks(chunks, doc)
    f.delete_purge_2(engine, target_chunks)
    for chunk in target_chunks[:100]:
        f.chunks_delete_2(ctx, chunk)
    if f.has_more_target_chunks(target_chunks):
        return "pending"
    target_runs = f.select_target_runs(runs, doc)
    for run in target_runs[:100]:
        f.ocr_runs_delete(ctx, run)
    if f.has_more_target_ocr(target_runs):
        return "pending"
    for asset in assets:
        if f.is_target_asset(asset, doc):
            f.assets_delete(ctx, asset)
    for draft in drafts:
        if f.is_target_draft(draft, doc):
            f.drafts_delete(ctx, draft)
    return "done"


def process(ctx: Context, engine: Engine, job_id: str) -> models.OutboxRow:
    """権限と再試行上限を確認して配送し、成功・失敗状態を記録する。"""
    f.require_operator(ctx)
    rows = f.outbox_get(ctx, job_id)
    f.require_job(rows)
    job = rows[0]
    f.enforce_retry_limit(job)
    if f.is_finished_job(job):
        return job
    try:
        status = purge(ctx, job, engine) if f.is_purge_job(job) else build_index(ctx, job, engine)
        updated = f.build_updated(job, status)
    except Problem as exc:
        ops_logger.error(
            MessageId.INDEX_FAILED, context_model=continuation_context(MessageId.INDEX_FAILED, exc)
        )
        updated = f.build_updated_2(job, exc)
    except (OSError, BotoCoreError, ClientError) as exc:
        ops_logger.error(
            MessageId.INDEX_FAILED, context_model=continuation_context(MessageId.INDEX_FAILED, exc)
        )
        updated = f.build_updated_3(job)
    f.outbox_update(ctx, updated)
    f.check_concurrent_access(ctx)
    return updated
