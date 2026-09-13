"""indexingのsharedの業務判定と処理を実行する。"""

from __future__ import annotations

import json
from collections.abc import Sequence

import kotorelay.context as context_types
import kotorelay.engines as engine_types
import kotorelay.errors as error_types
import kotorelay.generated.models as models
import kotorelay.operations.indexing.shared.generated.queries as q
import kotorelay.schemas as shared_schemas
from kotorelay.context import now, stable_id
from kotorelay.errors import require
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


def documents_get(ctx: context_types.Context, job: models.OutboxRow) -> list[q.DocumentsGetRow]:
    """現在の組織に属する指定の文書について、文書の所有部署・公開範囲・状態・公開版の参照を取得する。"""
    return q.documents_get(
        ctx.db, q.DocumentsGetParams(organization_id=ctx.org, id=job.document_id)
    )


def is_obsolete_version(doc: q.DocumentsGetRow, job: models.OutboxRow) -> bool:
    """ジョブの対象版が現在の公開版ではないかを判定する。"""
    return bool(doc.latest_version_id != job.version_id or not job.version_id)


def select_stale(
    ctx: context_types.Context, doc: q.DocumentsGetRow, job: models.OutboxRow
) -> list[q.ChunksListRow]:
    """用途と対象に一致するデータだけを取り出す。"""
    return [
        c
        for c in q.chunks_list(ctx.db, q.ChunksListParams(organization_id=ctx.org))
        if c.document_id == doc.id and (doc.status != "active" or c.version_id != job.version_id)
    ]


def delete_build_index(engine: engine_types.Engine, stale: list[q.ChunksListRow]) -> None:
    """不要になった実体または検索索引を削除する。"""
    return engine.delete([c.id for c in stale[:100]])


def chunks_delete(ctx: context_types.Context, stale_chunk: q.ChunksListRow) -> int:
    """現在の組織に属する指定の検索用の文書断片の記録を削除する。"""
    return q.chunks_delete(ctx.db, q.ChunksDeleteParams(organization_id=ctx.org, id=stale_chunk.id))


def has_more_stale_chunks(stale: list[q.ChunksListRow]) -> bool:
    """一回の削除上限を超える古い断片が残っているかを判定する。"""
    return bool(len(stale) > 100)


def is_inactive_document(doc: q.DocumentsGetRow) -> bool:
    """索引対象の文書が有効状態ではないかを判定する。"""
    return bool(doc.status != "active")


def versions_get(ctx: context_types.Context, version_id: str) -> list[q.VersionsGetRow]:
    """現在の組織に属する指定の文書版について、確定した本文の保存先と画像構成・検証用ハッシュを取得する。"""
    return q.versions_get(ctx.db, q.VersionsGetParams(organization_id=ctx.org, id=version_id))


def build_manifest(version: q.VersionsGetRow) -> shared_schemas.Manifest:
    """後続処理に渡すデータを組み立てる。"""
    return Manifest.model_validate_json(version.manifest)


def decode_body(version: q.VersionsGetRow, ctx: context_types.Context) -> str:
    """保存された実体をテキストへ復元する。"""
    return ctx.objects.get(version.body_key, version.body_hash).decode()


def select_parts(body: str) -> list[tuple[str, str, str]]:
    """用途と対象に一致するデータだけを取り出す。"""
    return [(heading, text, "[]") for heading, text in split_chunks(body)]


def assets_get(
    ctx: context_types.Context, image: shared_schemas.ManifestImage
) -> list[q.AssetsGetRow]:
    """現在の組織に属する指定の添付画像について、画像の保存先・形式・寸法・検証用ハッシュを取得する。"""
    return q.assets_get(
        ctx.db, q.AssetsGetParams(organization_id=ctx.org, id=image.placement.asset_id)
    )


def ocr_runs_get(
    ctx: context_types.Context, image: shared_schemas.ManifestImage
) -> list[q.OcrRunsGetRow]:
    """現在の組織に属する指定の文字認識の実行記録について、認識結果の保存先・検証用ハッシュ・確認状態を取得する。"""
    return q.ocr_runs_get(
        ctx.db, q.OcrRunsGetParams(organization_id=ctx.org, id=image.placement.ocr_run_id)
    )


def get_build_index(
    asset: q.AssetsGetRow, image: shared_schemas.ManifestImage, ctx: context_types.Context
) -> bytes:
    """記録された保存先から実体を取得してハッシュを照合する。"""
    return ctx.objects.get(asset.object_key, image.image_hash)


def build_result(
    run: q.OcrRunsGetRow, image: shared_schemas.ManifestImage, ctx: context_types.Context
) -> shared_schemas.OcrResult:
    """後続処理に渡すデータを組み立てる。"""
    return OcrResult.model_validate_json(ctx.objects.get(run.result_key, image.ocr_hash))


def enforce_chunk_limit(parts: list[tuple[str, str, str]]) -> None:
    """生成する検索断片の件数上限を確認する。"""
    return require(len(parts) <= 300, "limit", 422)


def map_previous(
    ctx: context_types.Context, version: q.VersionsGetRow
) -> dict[str, q.ChunksListRow]:
    """取得したデータを識別子別に参照できる辞書へ変換する。"""
    return {
        c.id: c
        for c in q.chunks_list(ctx.db, q.ChunksListParams(organization_id=ctx.org))
        if c.version_id == version.id
    }


def put_key(ctx: context_types.Context, text: str) -> str:
    """本文または画像の実体を保存して内容ハッシュのキーを取得する。"""
    return ctx.objects.put(text.encode(), "text/plain")


def build_chunk(
    key: str,
    heading: str,
    placements: str,
    ctx: context_types.Context,
    doc: q.DocumentsGetRow,
    version: q.VersionsGetRow,
    number: int,
) -> models.ChunksRow:
    """後続処理に渡すデータを組み立てる。"""
    return models.ChunksRow(
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


def index_build_index(
    text: str,
    engine: engine_types.Engine,
    chunk: models.ChunksRow,
    doc: q.DocumentsGetRow,
    version: q.VersionsGetRow,
) -> None:
    """文書断片を検索エンジンへ登録する。"""
    return engine.index(chunk.id, text, doc.id, version.id)


def is_existing_chunk(previous: dict[str, q.ChunksListRow], chunk: models.ChunksRow) -> bool:
    """同じ識別子の検索断片が既に存在するかを判定する。"""
    return bool(chunk.id in previous)


def chunks_update(ctx: context_types.Context, chunk: models.ChunksRow) -> int:
    """現在の組織に属する指定の検索用の文書断片について、本文の保存先・出典の版・画像配置・索引反映状態を更新する。"""
    return q.chunks_update(ctx.db, q.ChunksUpdateParams.model_validate(chunk, from_attributes=True))


def chunks_insert(ctx: context_types.Context, chunk: models.ChunksRow) -> int:
    """現在の組織の検索用の文書断片を、出典の版・本文の保存先・画像配置とともに登録する。"""
    return q.chunks_insert(ctx.db, q.ChunksInsertParams.model_validate(chunk, from_attributes=True))


def select_actual(ctx: context_types.Context, version: q.VersionsGetRow) -> list[q.ChunksListRow]:
    """用途と対象に一致するデータだけを取り出す。"""
    return [
        c
        for c in q.chunks_list(ctx.db, q.ChunksListParams(organization_id=ctx.org))
        if c.version_id == version.id
    ]


def verify_index_completion(
    actual: list[q.ChunksListRow], parts: list[tuple[str, str, str]], engine: engine_types.Engine
) -> None:
    """保存件数と検索エンジンの反映状態が一致することを確認する。"""
    return require(
        len(actual) == len(parts) and engine.verify([c.id for c in actual]), "integrity", 503
    )


def get_build_index_2(current: q.ChunksListRow, ctx: context_types.Context) -> bytes:
    """記録された保存先から実体を取得してハッシュを照合する。"""
    return ctx.objects.get(current.body_key, current.sha256)


def chunks_update_2(ctx: context_types.Context, current: q.ChunksListRow) -> int:
    """現在の組織に属する指定の検索用の文書断片について、本文の保存先・出典の版・画像配置・索引反映状態を更新する。"""
    return q.chunks_update(
        ctx.db,
        q.ChunksUpdateParams.model_validate(
            current.model_copy(update={"ready": True}), from_attributes=True
        ),
    )


def documents_get_2(ctx: context_types.Context, job: models.OutboxRow) -> list[q.DocumentsGetRow]:
    """現在の組織に属する指定の文書について、文書の所有部署・公開範囲・状態・公開版の参照を取得する。"""
    return q.documents_get(
        ctx.db, q.DocumentsGetParams(organization_id=ctx.org, id=job.document_id)
    )


def is_restored_document(doc: q.DocumentsGetRow) -> bool:
    """削除ジョブの対象文書が削除状態ではないかを判定する。"""
    return bool(doc.status != "deleted")


def is_within_retention(ctx: context_types.Context, job: models.OutboxRow) -> bool:
    """削除までの保存期間が経過していないかを判定する。"""
    return bool((now() - job.created_at).total_seconds() < ctx.settings.retention_days * 86400)


def chunks_list(ctx: context_types.Context) -> list[q.ChunksListRow]:
    """現在の組織に属する検索用の文書断片を識別子順に一覧取得する。"""
    return q.chunks_list(ctx.db, q.ChunksListParams(organization_id=ctx.org))


def assets_list(ctx: context_types.Context) -> list[q.AssetsListRow]:
    """現在の組織に属する添付画像を識別子順に一覧取得する。"""
    return q.assets_list(ctx.db, q.AssetsListParams(organization_id=ctx.org))


def ocr_runs_list(ctx: context_types.Context) -> list[q.OcrRunsListRow]:
    """現在の組織に属する文字認識の実行記録を識別子順に一覧取得する。"""
    return q.ocr_runs_list(ctx.db, q.OcrRunsListParams(organization_id=ctx.org))


def drafts_list(ctx: context_types.Context) -> list[q.DraftsListRow]:
    """現在の組織に属する下書きを識別子順に一覧取得する。"""
    return q.drafts_list(ctx.db, q.DraftsListParams(organization_id=ctx.org))


def versions_list(ctx: context_types.Context) -> list[q.VersionsListRow]:
    """現在の組織に属する文書版を識別子順に一覧取得する。"""
    return q.versions_list(ctx.db, q.VersionsListParams(organization_id=ctx.org))


def answers_list(ctx: context_types.Context) -> list[q.AnswersListRow]:
    """現在の組織に属する回答履歴を識別子順に一覧取得する。"""
    return q.answers_list(ctx.db, q.AnswersListParams(organization_id=ctx.org))


def collect_live(ctx: context_types.Context) -> set[str]:
    """処理対象の識別子を重複なく取り出す。"""
    return {
        d.id
        for d in q.documents_list(ctx.db, q.DocumentsListParams(organization_id=ctx.org))
        if d.status != "deleted"
    }


def delete_purge(key: str, ctx: context_types.Context) -> None:
    """不要になった実体または検索索引を削除する。"""
    return ctx.objects.delete(key)


def select_target_chunks(
    chunks: list[q.ChunksListRow], doc: q.DocumentsGetRow
) -> list[q.ChunksListRow]:
    """用途と対象に一致するデータだけを取り出す。"""
    return [c for c in chunks if c.document_id == doc.id]


def delete_purge_2(engine: engine_types.Engine, target_chunks: list[q.ChunksListRow]) -> None:
    """不要になった実体または検索索引を削除する。"""
    return engine.delete([c.id for c in target_chunks])


def chunks_delete_2(ctx: context_types.Context, chunk: q.ChunksListRow) -> int:
    """現在の組織に属する指定の検索用の文書断片の記録を削除する。"""
    return q.chunks_delete(ctx.db, q.ChunksDeleteParams(organization_id=ctx.org, id=chunk.id))


def has_more_target_chunks(target_chunks: list[q.ChunksListRow]) -> bool:
    """一回の上限を超える削除対象の断片が残っているかを判定する。"""
    return bool(len(target_chunks) > 100)


def select_target_runs(
    runs: list[q.OcrRunsListRow], doc: q.DocumentsGetRow
) -> list[q.OcrRunsListRow]:
    """用途と対象に一致するデータだけを取り出す。"""
    return [r for r in runs if r.document_id == doc.id]


def ocr_runs_delete(ctx: context_types.Context, run: q.OcrRunsListRow) -> int:
    """現在の組織に属する指定の文字認識の実行記録の記録を削除する。"""
    return q.ocr_runs_delete(ctx.db, q.OcrRunsDeleteParams(organization_id=ctx.org, id=run.id))


def has_more_target_ocr(target_runs: list[q.OcrRunsListRow]) -> bool:
    """一回の上限を超える削除対象のOCR記録が残っているかを判定する。"""
    return bool(len(target_runs) > 100)


def is_target_asset(asset: q.AssetsListRow, doc: q.DocumentsGetRow) -> bool:
    """添付画像が削除対象の文書に属するかを判定する。"""
    return bool(asset.document_id == doc.id)


def assets_delete(ctx: context_types.Context, asset: q.AssetsListRow) -> int:
    """現在の組織に属する指定の添付画像の記録を削除する。"""
    return q.assets_delete(ctx.db, q.AssetsDeleteParams(organization_id=ctx.org, id=asset.id))


def is_target_draft(draft: q.DraftsListRow, doc: q.DocumentsGetRow) -> bool:
    """下書きが削除対象の文書に属するかを判定する。"""
    return bool(draft.document_id == doc.id)


def drafts_delete(ctx: context_types.Context, draft: q.DraftsListRow) -> int:
    """現在の組織に属する指定の下書きの記録を削除する。"""
    return q.drafts_delete(ctx.db, q.DraftsDeleteParams(organization_id=ctx.org, id=draft.id))


def require_operator(ctx: context_types.Context) -> None:
    """ジョブを実行できる運用権限を確認する。"""
    return require(ctx.user.operator, "forbidden", 403)


def outbox_get(ctx: context_types.Context, job_id: str) -> list[q.OutboxGetRow]:
    """現在の組織に属する指定の反映・削除ジョブについて、対象文書と版・処理種別・進行状態・試行回数を取得する。"""
    return q.outbox_get(ctx.db, q.OutboxGetParams(organization_id=ctx.org, id=job_id))


def require_job(rows: list[q.OutboxGetRow]) -> None:
    """実行対象のジョブが存在することを確認する。"""
    return require(bool(rows))


def enforce_retry_limit(job: q.OutboxGetRow) -> None:
    """ジョブの再試行回数の上限を確認する。"""
    return require(job.attempts < 5, "limit", 429)


def is_finished_job(job: q.OutboxGetRow) -> bool:
    """ジョブが完了または旧版として終了しているかを判定する。"""
    return bool(job.status in {"done", "obsolete"})


def build_updated(job: q.OutboxGetRow, status: str) -> q.OutboxGetRow:
    """後続処理に渡すデータを組み立てる。"""
    return job.model_copy(
        update={
            "status": status,
            "attempts": job.attempts if status in {"retained", "pending"} else job.attempts + 1,
            "error_code": "",
        }
    )


def build_updated_2(job: q.OutboxGetRow, exc: error_types.Problem) -> q.OutboxGetRow:
    """後続処理に渡すデータを組み立てる。"""
    return job.model_copy(
        update={"status": "failed", "attempts": job.attempts + 1, "error_code": exc.code}
    )


def build_updated_3(job: q.OutboxGetRow) -> q.OutboxGetRow:
    """後続処理に渡すデータを組み立てる。"""
    return job.model_copy(
        update={"status": "failed", "attempts": job.attempts + 1, "error_code": "external_failure"}
    )


def outbox_update(ctx: context_types.Context, updated: q.OutboxGetRow) -> int:
    """現在の組織に属する指定の反映・削除ジョブについて、対象文書と版・処理種別・進行状態・試行回数を更新する。"""
    return q.outbox_update(
        ctx.db, q.OutboxUpdateParams.model_validate(updated, from_attributes=True)
    )


def check_concurrent_access(ctx: context_types.Context) -> None:
    """組織の更新競合を検出するための書込みフェンスを更新する。"""
    return ctx.fence()


def image_chunks(
    result: shared_schemas.OcrResult, image: shared_schemas.ManifestImage
) -> list[tuple[str, str, str]]:
    """OCRの領域順に本文を復元し、画像配置を付けた検索断片へ分割する。"""
    text = "\n".join(
        region.text for region in sorted(result.regions, key=lambda region: region.order)
    )
    return [
        (image.placement.heading or heading, text, json.dumps([image.placement.id]))
        for heading, text in split_chunks(text or "添付画像")
    ]


def is_purge_job(job: models.OutboxRow) -> bool:
    """ジョブが保存期間後の実体削除を要求しているかを判定する。"""
    return job.kind == "purge"


def collect_object_keys(
    document_id: str,
    live: set[str],
    chunks: Sequence[models.ChunksRow],
    assets: Sequence[models.AssetsRow],
    runs: Sequence[models.OcrRunsRow],
    drafts: Sequence[models.DraftsRow],
    versions: Sequence[models.VersionsRow],
    answers: Sequence[models.AnswersRow],
) -> tuple[set[str], set[str]]:
    """削除文書の実体参照と、他文書・質問が引き続き使う保護対象を分類する。"""
    keys: set[str] = set()
    protected: set[str] = set()
    sources: list[
        tuple[
            Sequence[
                models.ChunksRow
                | models.AssetsRow
                | models.OcrRunsRow
                | models.DraftsRow
                | models.VersionsRow
            ],
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
            if row.document_id == document_id:
                keys.add(str(getattr(row, column)))
            elif row.document_id in live:
                protected.add(str(getattr(row, column)))
    for answer in answers:
        evidence = shared_schemas.Evidence.model_validate_json(answer.evidence)
        target = (
            keys if any(c.document_id == document_id for c in evidence.citations) else protected
        )
        target.add(answer.answer_key)
        protected.add(answer.question_key)
    return (keys, protected)
