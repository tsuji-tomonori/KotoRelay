"""chatのsharedの業務判定と処理を実行する。"""

from __future__ import annotations

import json

from kotorelay.context import Context
from kotorelay.errors import Problem, require
from kotorelay.generated import models
from kotorelay.objects import digest
from kotorelay.operational_logging import MessageId, continuation_context, ops_logger
from kotorelay.operations.chat.shared.generated import queries as q
from kotorelay.schemas import AnswerView, Citation, Evidence, Manifest


def validate_citation(ctx: Context, citation: Citation) -> bool:
    """閲覧権限・現行版・根拠の実体とハッシュが現在も有効かを判定する。"""
    docs = q.documents_get(
        ctx.db, q.DocumentsGetParams(organization_id=ctx.org, id=citation.document_id)
    )
    if not docs:
        return False
    doc = docs[0]
    if (
        not ctx.can_read(doc)
        or doc.latest_version_id != citation.version_id
        or doc.revision != citation.document_revision
    ):
        return False
    versions = q.versions_get(
        ctx.db, q.VersionsGetParams(organization_id=ctx.org, id=citation.version_id)
    )
    chunks = q.chunks_get(ctx.db, q.ChunksGetParams(organization_id=ctx.org, id=citation.chunk_id))
    if not versions or not chunks:
        return False
    version, chunk = (versions[0], chunks[0])
    if not (
        digest(version.manifest.encode()) == version.manifest_hash
        and version.document_id == doc.id
        and chunk.ready
        and (chunk.version_id == version.id)
        and (chunk.document_id == doc.id)
        and (chunk.manifest_hash == version.manifest_hash == citation.manifest_hash)
        and (chunk.sha256 == citation.chunk_hash)
    ):
        return False
    try:
        ctx.objects.get(chunk.body_key, chunk.sha256)
        ctx.objects.get(version.body_key, version.body_hash)
        manifest = Manifest.model_validate_json(version.manifest)
        placements = set(json.loads(chunk.placements))
        if placements - {image.placement.id for image in manifest.images}:
            return False
        for image in manifest.images:
            if image.placement.id in json.loads(chunk.placements):
                assets = q.assets_get(
                    ctx.db, q.AssetsGetParams(organization_id=ctx.org, id=image.placement.asset_id)
                )
                runs = q.ocr_runs_get(
                    ctx.db,
                    q.OcrRunsGetParams(organization_id=ctx.org, id=image.placement.ocr_run_id),
                )
                if not assets or not runs or (not runs[0].confirmed) or (runs[0].status != "ready"):
                    return False
                ctx.objects.get(assets[0].object_key, image.image_hash)
                ctx.objects.get(runs[0].result_key, image.ocr_hash)
        return True
    except (Problem, ValueError) as exc:
        ops_logger.warning(
            MessageId.EVIDENCE_REJECTED,
            context_model=continuation_context(MessageId.EVIDENCE_REJECTED, exc),
        )
        return False


def present(ctx: Context, answer: models.AnswersRow) -> AnswerView:
    """現在の根拠の有効性に応じて回答履歴と引用の表示を組み立てる。"""
    require(answer.user_id == ctx.user.id)
    evidence = Evidence.model_validate_json(answer.evidence)
    valid = all(validate_citation(ctx, c) for c in evidence.citations)
    return AnswerView(
        id=answer.id,
        conversation_id=answer.conversation_id,
        question=ctx.objects.get(answer.question_key).decode(),
        answer=ctx.objects.get(answer.answer_key).decode()
        if valid
        else "権限または公開版が変更されたため、この回答は表示できません。",
        status=answer.status if valid else "hidden",
        citations=evidence.citations if valid else [],
        model=answer.model,
        created_at=answer.created_at,
    )
