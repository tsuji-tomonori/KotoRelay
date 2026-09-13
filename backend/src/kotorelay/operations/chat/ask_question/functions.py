"""chatのask_questionの業務判定と処理を実行する。"""

from __future__ import annotations

import datetime as datetime_module
import json

import kotorelay.context as context_types
import kotorelay.engines as engine_types
import kotorelay.errors as error_types
import kotorelay.generated.models as models
import kotorelay.operations.chat.ask_question.generated.queries as q
import kotorelay.operations.chat.ask_question.schemas as request_schemas
import kotorelay.runtime as runtime_types
import kotorelay.schemas as shared_schemas
from kotorelay.context import now, stable_id
from kotorelay.engines import terms
from kotorelay.errors import require
from kotorelay.operations.chat.ask_question.schemas import Prepared
from kotorelay.schemas import Evidence, Manifest


def is_unhandled_problem(exc: error_types.Problem) -> bool:
    """既存回答の再表示以外の例外かを判定する。"""
    return bool(exc.code != "already_answered")


def answers_get(ctx: context_types.Context, exc: error_types.Problem) -> list[q.AnswersGetRow]:
    """現在の組織に属する指定の回答履歴について、質問・回答の保存先と根拠・回答状態を取得する。"""
    return q.answers_get(ctx.db, q.AnswersGetParams(organization_id=ctx.org, id=exc.message))


def discard_invalid_evidence(prepared: Prepared) -> Prepared:
    """失効した根拠とその本文・画像をモデル入力から除く。"""
    return prepared.model_copy(update={"citations": [], "texts": [], "images": []})


def generate_answer(prepared: Prepared, rt: runtime_types.Runtime) -> str:
    """準備済みの本文と画像をモデルへ送り回答を取得する。"""
    return rt.engine.generate(prepared.question, prepared.texts, prepared.images)


def require_question_membership(ctx: context_types.Context, data: request_schemas.Ask) -> None:
    """質問先部署への現在の所属を確認する。"""
    return require(ctx.member(data.department_id), "forbidden", 403)


def answers_get_2(ctx: context_types.Context, answer_id: str) -> list[q.AnswersGetRow]:
    """現在の組織に属する指定の回答履歴について、質問・回答の保存先と根拠・回答状態を取得する。"""
    return q.answers_get(ctx.db, q.AnswersGetParams(organization_id=ctx.org, id=answer_id))


def validate_repeated_question(
    data: request_schemas.Ask, prior: list[q.AnswersGetRow], ctx: context_types.Context
) -> None:
    """同じ冪等キーの質問内容・部署・会話が一致することを確認する。"""
    return require(
        prior[0].user_id == ctx.user.id
        and ctx.objects.get(prior[0].question_key).decode() == data.question
        and (prior[0].department_id == data.department_id)
        and (data.conversation_id is None or data.conversation_id == prior[0].conversation_id),
        "idempotency_conflict",
        409,
    )


def find_previous_result(key: str, request: str, ctx: context_types.Context) -> str | None:
    """要求内容の一致を確認して同じ冪等キーの記録済み結果を取得する。"""
    return ctx.idempotent_result(key, "ask", request)


def events_list(ctx: context_types.Context) -> list[q.EventsListRow]:
    """現在の組織に属する利用イベントを識別子順に一覧取得する。"""
    return q.events_list(ctx.db, q.EventsListParams(organization_id=ctx.org))


def enforce_daily_question_limit(
    resumed: str | None,
    ctx: context_types.Context,
    events: list[q.EventsListRow],
    today: datetime_module.date,
) -> None:
    """再開要求を除いて利用者の当日質問数の上限を確認する。"""
    return require(
        resumed is not None
        or sum(
            1
            for e in events
            if e.user_id == ctx.user.id and e.kind == "question" and (e.created_at.date() == today)
        )
        < ctx.settings.max_questions_per_day,
        "limit",
        429,
    )


def conversations_get(
    ctx: context_types.Context, conversation_id: str
) -> list[q.ConversationsGetRow]:
    """現在の組織に属する指定の会話について、会話の所有者と開始日時を取得する。"""
    return q.conversations_get(
        ctx.db, q.ConversationsGetParams(organization_id=ctx.org, id=conversation_id)
    )


def require_conversation_owner(
    conversations: list[q.ConversationsGetRow], ctx: context_types.Context
) -> None:
    """会話が存在し現在の利用者が所有することを確認する。"""
    return require(bool(conversations) and conversations[0].user_id == ctx.user.id)


def require_same_department(
    data: request_schemas.Ask, conversation_id: str, ctx: context_types.Context
) -> None:
    """会話内の回答が同じ部署に帰属することを確認する。"""
    return require(
        all(
            a.department_id == data.department_id
            for a in q.answers_list(ctx.db, q.AnswersListParams(organization_id=ctx.org))
            if a.conversation_id == conversation_id
        ),
        "conversation_department",
        409,
    )


def conversations_insert(ctx: context_types.Context, conversation_id: str) -> int:
    """現在の組織の会話を、所有者と開始日時を指定して登録する。"""
    return q.conversations_insert(
        ctx.db,
        q.ConversationsInsertParams(
            id=conversation_id, organization_id=ctx.org, user_id=ctx.user.id, created_at=now()
        ),
    )


def load_readable_documents(ctx: context_types.Context) -> dict[str, q.DocumentsListRow]:
    """最新承認版を持ち現在閲覧できる文書を識別子別に取得する。"""
    return {
        d.id: d
        for d in q.documents_list(ctx.db, q.DocumentsListParams(organization_id=ctx.org))
        if d.latest_version_id and ctx.can_read(d)
    }


def search_vector_keys(
    engine: engine_types.Engine, data: request_schemas.Ask, docs: dict[str, q.DocumentsListRow]
) -> list[str] | None:
    """閲覧可能な文書の範囲で質問に関連する断片を検索する。"""
    return engine.search(data.question, list(docs))


def chunks_list(ctx: context_types.Context) -> list[q.ChunksListRow]:
    """現在の組織に属する検索用の文書断片を識別子順に一覧取得する。"""
    return q.chunks_list(ctx.db, q.ChunksListParams(organization_id=ctx.org))


def is_unavailable_chunk(docs: dict[str, q.DocumentsListRow], chunk: models.ChunksRow) -> bool:
    """閲覧可能な最新承認版の反映済み断片でないかを判定する。"""
    return bool(
        chunk.document_id not in docs
        or chunk.version_id != docs[chunk.document_id].latest_version_id
        or (not chunk.ready)
    )


def is_outside_search_results(vector_keys: list[str] | None, chunk: models.ChunksRow) -> bool:
    """検索エンジンの候補に含まれない断片かを判定する。"""
    return bool(vector_keys is not None and chunk.id not in vector_keys)


def load_chunk_text(chunk: models.ChunksRow, ctx: context_types.Context) -> str:
    """断片実体のハッシュを照合して本文を取得する。"""
    return ctx.objects.get(chunk.body_key, chunk.sha256).decode()


def has_sufficient_relevance(
    score: float, vector_keys: list[str] | None, data: request_schemas.Ask
) -> bool:
    """質問と断片の関連度が採用基準を満たすかを判定する。"""
    return bool(
        score > 0 and (vector_keys is not None or score >= max(1, len(terms(data.question)) * 0.3))
    )


def versions_get(ctx: context_types.Context, chunk: models.ChunksRow) -> list[q.VersionsGetRow]:
    """現在の組織に属する指定の文書版について、確定した本文の保存先と画像構成・検証用ハッシュを取得する。"""
    return q.versions_get(ctx.db, q.VersionsGetParams(organization_id=ctx.org, id=chunk.version_id))


def parse_manifest(version: q.VersionsGetRow) -> shared_schemas.Manifest:
    """確定版に記録された本文と画像の構成を読み取る。"""
    return Manifest.model_validate_json(version.manifest)


def select_citation_images(
    manifest: shared_schemas.Manifest, chunk: models.ChunksRow
) -> list[shared_schemas.ManifestImage]:
    """検索断片に関連付けられた画像だけを取り出す。"""
    return [i for i in manifest.images if i.placement.id in json.loads(chunk.placements)]


def exceeds_image_limit(
    images: list[bytes], related: list[shared_schemas.ManifestImage], ctx: context_types.Context
) -> bool:
    """根拠画像を追加するとモデル入力の画像数上限を超えるかを判定する。"""
    return bool(len(images) + len(related) > ctx.settings.max_model_images)


def assets_get(
    ctx: context_types.Context, image: shared_schemas.ManifestImage
) -> list[q.AssetsGetRow]:
    """現在の組織に属する指定の添付画像について、画像の保存先・形式・寸法・検証用ハッシュを取得する。"""
    return q.assets_get(
        ctx.db, q.AssetsGetParams(organization_id=ctx.org, id=image.placement.asset_id)
    )


def load_citation_image(
    asset: q.AssetsGetRow, image: shared_schemas.ManifestImage, ctx: context_types.Context
) -> bytes:
    """根拠画像のハッシュを照合してモデル入力用の実体を取得する。"""
    return ctx.objects.get(asset.object_key, image.image_hash)


def has_enough_citations(citations: list[shared_schemas.Citation]) -> bool:
    """回答に使用する根拠が五件に達したかを判定する。"""
    return bool(len(citations) >= 5)


def is_new_question(resumed: str | None) -> bool:
    """既存の受付記録を再開する要求ではないかを判定する。"""
    return bool(resumed is None)


def events_insert(ctx: context_types.Context, answer_id: str, data: request_schemas.Ask) -> int:
    """現在の組織の利用イベントとして、利用者・帰属部署・閲覧や質問の対象・結果・発生日時を登録する。"""
    return q.events_insert(
        ctx.db,
        q.EventsInsertParams(
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


def remember_prepare_result(
    key: str, request: str, conversation_id: str, ctx: context_types.Context
) -> None:
    """同じ要求を安全に再試行できるよう冪等キーと結果を記録する。"""
    return ctx.remember(key, "ask", request, conversation_id)


def check_concurrent_access(ctx: context_types.Context) -> None:
    """組織の更新競合を検出するための書込みフェンスを更新する。"""
    return ctx.fence()


def require_current_membership(ctx: context_types.Context, prepared: Prepared) -> None:
    """回答確定時点でも質問先部署への所属が有効であることを確認する。"""
    return require(ctx.member(prepared.department_id), "forbidden", 403)


def build_answer_record(
    status: str,
    prepared: Prepared,
    ctx: context_types.Context,
    engine: engine_types.Engine,
    text: str,
    citations: list[shared_schemas.Citation],
) -> models.AnswersRow:
    """回答状態に対応する質問・回答実体の保存先と根拠の行を組み立てる。"""
    return models.AnswersRow(
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


def answers_insert(ctx: context_types.Context, row: models.AnswersRow) -> int:
    """現在の組織の回答履歴として、質問者・利用部署・質問と回答の保存先・根拠を登録する。"""
    return q.answers_insert(ctx.db, q.AnswersInsertParams.model_validate(row, from_attributes=True))


def events_insert_2(
    ctx: context_types.Context, status: str, prepared: Prepared, row: models.AnswersRow
) -> int:
    """現在の組織の利用イベントとして、利用者・帰属部署・閲覧や質問の対象・結果・発生日時を登録する。"""
    return q.events_insert(
        ctx.db,
        q.EventsInsertParams(
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


def collect_contributing_documents(citations: list[shared_schemas.Citation]) -> set[str]:
    """回答根拠に寄与した文書の識別子を重複なく取り出す。"""
    return {c.document_id for c in citations}


def events_insert_3(
    ctx: context_types.Context,
    document_id: str,
    status: str,
    prepared: Prepared,
    row: models.AnswersRow,
) -> int:
    """現在の組織の利用イベントとして、利用者・帰属部署・閲覧や質問の対象・結果・発生日時を登録する。"""
    return q.events_insert(
        ctx.db,
        q.EventsInsertParams(
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


def record_finalize_audit(ctx: context_types.Context, status: str) -> None:
    """実行した変更の対象と結果を監査記録へ追加する。"""
    return ctx.audit("answer", after=status)


def score_chunk(question: str, text: str, vector_keys: list[str] | None, chunk_id: str) -> float:
    """検索順位があれば順位を使い、ローカル検索では質問と本文の共通語数を得点にする。"""
    return (
        float(len(terms(question) & terms(text)))
        if vector_keys is None
        else float(len(vector_keys) - vector_keys.index(chunk_id))
    )


def build_citation(
    doc: models.DocumentsRow, version: models.VersionsRow, chunk: models.ChunksRow
) -> shared_schemas.Citation:
    """取得時点の文書・版・断片とハッシュを回答根拠の参照値にまとめる。"""
    return shared_schemas.Citation(
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


def rank_candidates(
    scored: list[tuple[float, models.ChunksRow, str]],
) -> list[tuple[float, models.ChunksRow, str]]:
    """得点の降順と識別子の昇順で根拠候補を並べ、上位十件を取り出す。"""
    return sorted(scored, key=lambda item: (-item[0], item[1].id))[:10]


def resolve_answer_outcome(
    valid: bool, failed: bool, answer: str, evidence: list[shared_schemas.Citation]
) -> tuple[str, list[shared_schemas.Citation], str]:
    """生成失敗と根拠の有効性から回答状態・公開する根拠・利用者向け本文を決める。"""
    status = "failed" if failed else "answered" if valid else "held"
    return (
        status,
        evidence if status == "answered" else [],
        answer
        if status == "answered"
        else "現在利用できる根拠が不足しているため、回答を保留しました。",
    )
