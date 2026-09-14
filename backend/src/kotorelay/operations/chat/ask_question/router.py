"""ask_questionのHTTP入力と業務処理の順序を宣言する。"""

from __future__ import annotations

from datetime import UTC, datetime
from typing import cast

from botocore.exceptions import BotoCoreError, ClientError
from fastapi import APIRouter

from kotorelay.context import new_id, stable_id
from kotorelay.errors import Problem
from kotorelay.generated import models
from kotorelay.http_types import Key
from kotorelay.operational_logging import MessageId, continuation_context, ops_logger
from kotorelay.operations.chat.ask_question import functions as f
from kotorelay.operations.chat.ask_question.contract import CONTRACT
from kotorelay.operations.chat.ask_question.response_builders import build_response
from kotorelay.operations.chat.ask_question.samples import SAMPLES
from kotorelay.operations.chat.ask_question.schemas import Ask, Prepared
from kotorelay.operations.chat.shared import functions as evidence_functions
from kotorelay.operations.chat.shared.functions import present
from kotorelay.runtime import Rt, Subject
from kotorelay.schemas import AnswerView, Citation

router = APIRouter(prefix="/api/chat", tags=["RAGチャット"])


@router.post(
    "",
    summary="最新承認版の根拠で回答",
    operation_id="ask_question",
    openapi_extra=CONTRACT.openapi_extra(SAMPLES),
)
def ask_question(rt: Rt, subject: Subject, data: Ask, key: Key) -> AnswerView:
    """受付を確定し、transaction外で生成して再認可後に回答を保存する。"""
    try:
        with rt.context(subject) as ctx:
            f.require_question_membership(ctx, data)
            answer_id = stable_id(ctx.user.id + str(key))
            prior = f.answers_get_2(ctx, answer_id)
            if f.has_previous_answer(prior):
                f.validate_repeated_question(data, prior, ctx)
                raise Problem(409, "already_answered", answer_id)
            request = data.model_dump_json()
            resumed = f.find_previous_result(str(key), request, ctx)
            events = f.events_list(ctx)
            today = datetime.now(UTC).date()
            f.enforce_daily_question_limit(resumed, ctx, events, today)
            if f.has_prepared_conversation(resumed):
                conversation_id = cast(str, resumed)
            elif f.has_requested_conversation(data):
                conversations = f.conversations_get(ctx, cast(str, data.conversation_id))
                f.require_conversation_owner(conversations, ctx)
                conversation_id = conversations[0].id
                f.require_same_department(data, conversation_id, ctx)
            else:
                conversation_id = new_id()
                f.conversations_insert(ctx, conversation_id)
            docs = f.load_readable_documents(ctx)
            vector_keys = f.search_vector_keys(rt.engine, data, docs)
            scored: list[tuple[float, models.ChunksRow, str]] = []
            chunk: models.ChunksRow
            for chunk in f.chunks_list(ctx):
                if f.is_unavailable_chunk(docs, chunk):
                    continue
                if f.is_outside_search_results(vector_keys, chunk):
                    continue
                try:
                    text = f.load_chunk_text(chunk, ctx)
                except Problem as exc:
                    ops_logger.warning(
                        MessageId.EVIDENCE_REJECTED,
                        context_model=continuation_context(MessageId.EVIDENCE_REJECTED, exc),
                    )
                    continue
                score = f.score_chunk(data.question, text, vector_keys, chunk.id)
                if f.has_sufficient_relevance(score, vector_keys, data):
                    scored.append((score, chunk, text))
            citations: list[Citation] = []
            texts: list[str] = []
            images: list[bytes] = []
            for _, chunk, text in f.rank_candidates(scored):
                doc = docs[chunk.document_id]
                version = f.versions_get(ctx, chunk)[0]
                citation = f.build_citation(doc, version, chunk)
                if not evidence_functions.validate_citation(ctx, citation):
                    continue
                manifest = f.parse_manifest(version)
                related = f.select_citation_images(manifest, chunk)
                if f.exceeds_image_limit(images, related, ctx):
                    continue
                for image in related:
                    asset = f.assets_get(ctx, image)[0]
                    images.append(f.load_citation_image(asset, image, ctx))
                citations.append(citation)
                texts.append(text)
                if f.has_enough_citations(citations):
                    break
            if f.is_new_question(resumed):
                f.events_insert(ctx, answer_id, data)
                f.remember_prepare_result(str(key), request, conversation_id, ctx)
            f.check_concurrent_access(ctx)
            prepared = Prepared(
                answer_id=answer_id,
                conversation_id=conversation_id,
                question=data.question,
                department_id=data.department_id,
                citations=citations,
                texts=texts,
                images=images,
            )
    except Problem as exc:
        if f.is_unhandled_problem(exc):
            raise
        with rt.context(subject) as ctx:
            return build_response(present(ctx, f.answers_get(ctx, exc)[0]))
    failed = False
    answer = ""
    if f.has_answer_evidence(prepared):
        with rt.context(subject) as ctx:
            if not f.has_valid_evidence(ctx, prepared.citations):
                prepared = f.discard_invalid_evidence(prepared)
        if f.has_answer_evidence(prepared):
            try:
                answer = f.generate_answer(prepared, rt)
            except (BotoCoreError, ClientError, TimeoutError) as exc:
                ops_logger.error(
                    MessageId.MODEL_FAILED,
                    context_model=continuation_context(MessageId.MODEL_FAILED, exc),
                )
                failed = True
    with rt.context(subject) as ctx:
        f.require_current_membership(ctx, prepared)
        valid = f.has_answer_evidence(prepared) and f.has_valid_evidence(ctx, prepared.citations)
        status, citations, text = f.resolve_answer_outcome(
            valid, failed, answer, prepared.citations
        )
        row = f.build_answer_record(status, prepared, ctx, rt.engine, text, citations)
        f.answers_insert(ctx, row)
        f.events_insert_2(ctx, status, prepared, row)
        for document_id in f.collect_contributing_documents(citations):
            f.events_insert_3(ctx, document_id, status, prepared, row)
        f.record_finalize_audit(ctx, status)
        f.check_concurrent_access(ctx)
        return build_response(present(ctx, row))
