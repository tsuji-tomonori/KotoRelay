"""検索前・モデル入力前・回答確定時に現行の認可と版を検証する。"""

from __future__ import annotations

import json
from datetime import UTC, datetime

from pydantic import BaseModel

from kotorelay.context import Context, new_id, now, stable_id
from kotorelay.engines import Engine, terms
from kotorelay.errors import Problem, require
from kotorelay.generated import queries as q
from kotorelay.schemas import AnswerView, Ask, Citation, Evidence, Manifest


class Prepared(BaseModel):
    answer_id: str
    conversation_id: str
    question: str
    department_id: str
    citations: list[Citation]
    texts: list[str]
    images: list[bytes]


def validate_citation(ctx: Context, citation: Citation) -> bool:
    docs = q.documents_get(ctx.db, ctx.org, citation.document_id)
    if not docs:
        return False
    doc = docs[0]
    if (
        not ctx.can_read(doc)
        or doc.latest_version_id != citation.version_id
        or doc.revision != citation.document_revision
    ):
        return False
    versions = q.versions_get(ctx.db, ctx.org, citation.version_id)
    chunks = q.chunks_get(ctx.db, ctx.org, citation.chunk_id)
    if not versions or not chunks:
        return False
    version, chunk = versions[0], chunks[0]
    if not (
        chunk.ready
        and chunk.version_id == version.id
        and chunk.document_id == doc.id
        and chunk.manifest_hash == version.manifest_hash == citation.manifest_hash
        and chunk.sha256 == citation.chunk_hash
    ):
        return False
    try:
        ctx.objects.get(chunk.body_key, chunk.sha256)
        ctx.objects.get(version.body_key, version.body_hash)
        manifest = Manifest.model_validate_json(version.manifest)
        for image in manifest.images:
            if image.placement.id in json.loads(chunk.placements):
                assets = q.assets_get(ctx.db, ctx.org, image.placement.asset_id)
                runs = q.ocr_runs_get(ctx.db, ctx.org, image.placement.ocr_run_id)
                if not assets or not runs or not runs[0].confirmed or runs[0].status != "ready":
                    return False
                ctx.objects.get(assets[0].object_key, image.image_hash)
                ctx.objects.get(runs[0].result_key, image.ocr_hash)
        return True
    except (Problem, ValueError):
        return False


def prepare(ctx: Context, data: Ask, key: str, engine: Engine) -> Prepared:
    require(ctx.member(data.department_id), "forbidden", 403)
    answer_id = stable_id(ctx.user.id + key)
    prior = q.answers_get(ctx.db, ctx.org, answer_id)
    if prior:
        require(
            prior[0].user_id == ctx.user.id
            and ctx.objects.get(prior[0].question_key).decode() == data.question
            and prior[0].department_id == data.department_id
            and (data.conversation_id is None or data.conversation_id == prior[0].conversation_id),
            "idempotency_conflict",
            409,
        )
        raise Problem(409, "already_answered", answer_id)
    events = q.events_list(ctx.db, ctx.org)
    today = datetime.now(UTC).date()
    require(
        sum(
            1
            for e in events
            if e.user_id == ctx.user.id and e.kind == "question" and e.created_at.date() == today
        )
        < ctx.settings.max_questions_per_day,
        "limit",
        429,
    )
    if data.conversation_id:
        conversations = q.conversations_get(ctx.db, ctx.org, data.conversation_id)
        require(bool(conversations) and conversations[0].user_id == ctx.user.id)
        conversation_id = conversations[0].id
    else:
        conversation_id = new_id()
        q.conversations_insert(
            ctx.db,
            q.ConversationsRow(
                id=conversation_id, organization_id=ctx.org, user_id=ctx.user.id, created_at=now()
            ),
        )
    docs = {
        d.id: d
        for d in q.documents_list(ctx.db, ctx.org)
        if d.latest_version_id and ctx.can_read(d)
    }
    vector_keys = engine.search(data.question, list(docs))
    scored: list[tuple[float, q.ChunksRow, str]] = []
    for chunk in q.chunks_list(ctx.db, ctx.org):
        if (
            chunk.document_id not in docs
            or chunk.version_id != docs[chunk.document_id].latest_version_id
            or not chunk.ready
        ):
            continue
        if vector_keys is not None and chunk.id not in vector_keys:
            continue
        try:
            text = ctx.objects.get(chunk.body_key, chunk.sha256).decode()
        except Problem:
            continue
        score = (
            float(len(terms(data.question) & terms(text)))
            if vector_keys is None
            else float(len(vector_keys) - vector_keys.index(chunk.id))
        )
        if score > 0 and (
            vector_keys is not None or score >= max(1, len(terms(data.question)) * 0.3)
        ):
            scored.append((score, chunk, text))
    citations: list[Citation] = []
    texts: list[str] = []
    images: list[bytes] = []
    for _, chunk, text in sorted(scored, key=lambda item: (-item[0], item[1].id))[:10]:
        doc = docs[chunk.document_id]
        version = q.versions_get(ctx.db, ctx.org, chunk.version_id)[0]
        citation = Citation(
            document_id=doc.id,
            version_id=version.id,
            chunk_id=chunk.id,
            title=version.title,
            heading=chunk.heading,
            manifest_hash=version.manifest_hash,
            chunk_hash=chunk.sha256,
            document_revision=doc.revision,
        )
        if not validate_citation(ctx, citation):
            continue
        manifest = Manifest.model_validate_json(version.manifest)
        related = [i for i in manifest.images if i.placement.id in json.loads(chunk.placements)]
        if len(images) + len(related) > ctx.settings.max_model_images:
            continue
        for image in related:
            asset = q.assets_get(ctx.db, ctx.org, image.placement.asset_id)[0]
            images.append(ctx.objects.get(asset.object_key, image.image_hash))
        citations.append(citation)
        texts.append(text)
        if len(citations) >= 5:
            break
    q.events_insert(
        ctx.db,
        q.EventsRow(
            id=answer_id,
            organization_id=ctx.org,
            user_id=ctx.user.id,
            department_id=data.department_id,
            document_id=None,
            answer_id=None,
            kind="question",
            outcome="accepted",
            created_at=now(),
        ),
    )
    ctx.fence()
    return Prepared(
        answer_id=answer_id,
        conversation_id=conversation_id,
        question=data.question,
        department_id=data.department_id,
        citations=citations,
        texts=texts,
        images=images,
    )


def finalize(
    ctx: Context, prepared: Prepared, answer: str, engine: Engine, failed: bool = False
) -> AnswerView:
    require(ctx.member(prepared.department_id), "forbidden", 403)
    valid = bool(prepared.citations) and all(validate_citation(ctx, c) for c in prepared.citations)
    status = "failed" if failed else ("answered" if valid else "held")
    citations = prepared.citations if status == "answered" else []
    text = (
        answer
        if status == "answered"
        else "現在利用できる根拠が不足しているため、回答を保留しました。"
    )
    row = q.AnswersRow(
        id=prepared.answer_id,
        organization_id=ctx.org,
        conversation_id=prepared.conversation_id,
        user_id=ctx.user.id,
        department_id=prepared.department_id,
        question_key=ctx.objects.put(prepared.question.encode()),
        answer_key=ctx.objects.put(text.encode()),
        evidence=Evidence(citations=citations).model_dump_json(),
        status=status,
        model=engine.name,
        created_at=now(),
    )
    q.answers_insert(ctx.db, row)
    q.events_insert(
        ctx.db,
        q.EventsRow(
            id=stable_id(row.id + "outcome"),
            organization_id=ctx.org,
            user_id=ctx.user.id,
            department_id=prepared.department_id,
            document_id=None,
            answer_id=row.id,
            kind="outcome",
            outcome=status,
            created_at=now(),
        ),
    )
    for document_id in {c.document_id for c in citations}:
        q.events_insert(
            ctx.db,
            q.EventsRow(
                id=stable_id(row.id + document_id),
                organization_id=ctx.org,
                user_id=ctx.user.id,
                department_id=prepared.department_id,
                document_id=document_id,
                answer_id=row.id,
                kind="contribution",
                outcome=status,
                created_at=now(),
            ),
        )
    ctx.audit("answer", after=status)
    ctx.fence()
    return present(ctx, row)


def present(ctx: Context, answer: q.AnswersRow) -> AnswerView:
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


def history(ctx: Context, conversation_id: str) -> list[AnswerView]:
    conversations = q.conversations_get(ctx.db, ctx.org, conversation_id)
    require(bool(conversations) and conversations[0].user_id == ctx.user.id)
    return [
        present(ctx, a)
        for a in sorted(q.answers_list(ctx.db, ctx.org), key=lambda a: a.created_at)
        if a.conversation_id == conversation_id
    ]
