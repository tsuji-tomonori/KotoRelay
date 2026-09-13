"""chatのask_questionの業務判定と処理を実行する。"""

from __future__ import annotations

import json
from datetime import UTC, datetime

from botocore.exceptions import BotoCoreError, ClientError
from pydantic import BaseModel

from kotorelay.context import Context, new_id, now, stable_id
from kotorelay.engines import Engine, terms
from kotorelay.errors import Problem, require
from kotorelay.generated import models
from kotorelay.operations.chat.ask_question.generated import queries as q
from kotorelay.operations.chat.ask_question.schemas import Ask
from kotorelay.operations.chat.shared.functions import present, validate_citation
from kotorelay.runtime import Runtime
from kotorelay.schemas import AnswerView, Citation, Evidence, Manifest


class Prepared(BaseModel):
    answer_id: str
    conversation_id: str
    question: str
    department_id: str
    citations: list[Citation]
    texts: list[str]
    images: list[bytes]


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
    request = data.model_dump_json()
    resumed = ctx.idempotent_result(key, "ask", request)
    events = q.events_list(ctx.db, ctx.org)
    today = datetime.now(UTC).date()
    require(
        resumed is not None
        or sum(
            1
            for e in events
            if e.user_id == ctx.user.id and e.kind == "question" and e.created_at.date() == today
        )
        < ctx.settings.max_questions_per_day,
        "limit",
        429,
    )
    if resumed is not None:
        conversation_id = resumed
    elif data.conversation_id:
        conversations = q.conversations_get(ctx.db, ctx.org, data.conversation_id)
        require(bool(conversations) and conversations[0].user_id == ctx.user.id)
        conversation_id = conversations[0].id
        require(
            all(
                a.department_id == data.department_id
                for a in q.answers_list(ctx.db, ctx.org)
                if a.conversation_id == conversation_id
            ),
            "conversation_department",
            409,
        )
    else:
        conversation_id = new_id()
        q.conversations_insert(
            ctx.db,
            models.ConversationsRow(
                id=conversation_id, organization_id=ctx.org, user_id=ctx.user.id, created_at=now()
            ),
        )
    docs = {
        d.id: d
        for d in q.documents_list(ctx.db, ctx.org)
        if d.latest_version_id and ctx.can_read(d)
    }
    vector_keys = engine.search(data.question, list(docs))
    scored: list[tuple[float, models.ChunksRow, str]] = []
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
            version_number=version.number,
            has_images=bool(json.loads(chunk.placements)),
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
    if resumed is None:
        q.events_insert(
            ctx.db,
            models.EventsRow(
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
        ctx.remember(key, "ask", request, conversation_id)
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
    row = models.AnswersRow(
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
        models.EventsRow(
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
            models.EventsRow(
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


def ask(rt: Runtime, subject: str, data: Ask, key: str) -> AnswerView:
    try:
        with rt.context(subject) as ctx:
            prepared = prepare(ctx, data, key, rt.engine)
    except Problem as exc:
        if exc.code != "already_answered":
            raise
        with rt.context(subject) as ctx:
            return present(ctx, q.answers_get(ctx.db, ctx.org, exc.message)[0])
    failed = False
    answer = ""
    if prepared.citations:
        # 検索とモデル入力の間に確定した失効を改めて検出する。
        with rt.context(subject) as ctx:
            if not all(validate_citation(ctx, c) for c in prepared.citations):
                prepared = prepared.model_copy(update={"citations": [], "texts": [], "images": []})
        if prepared.citations:
            try:
                answer = rt.engine.generate(prepared.question, prepared.texts, prepared.images)
            except (BotoCoreError, ClientError, TimeoutError):
                failed = True
    with rt.context(subject) as ctx:
        return finalize(ctx, prepared, answer, rt.engine, failed)
