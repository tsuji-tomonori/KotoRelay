"""documentsのsubmit_versionの業務判定と処理を実行する。"""

from __future__ import annotations

import json
import uuid

import kotorelay.context as context_types
import kotorelay.generated.models as models
import kotorelay.operations.documents.submit_version.generated.queries as q
import kotorelay.operations.documents.submit_version.schemas as request_schemas
import kotorelay.schemas as shared_schemas
from kotorelay.context import new_id, now
from kotorelay.errors import require
from kotorelay.objects import digest
from kotorelay.schemas import Manifest, ManifestImage, Placement


def document_doc(ctx: context_types.Context, document_id: uuid.UUID) -> models.DocumentsRow:
    """文書を取得して要求された操作の権限を確認する。"""
    return ctx.document(str(document_id), "author")


def find_previous_result(request: str, ctx: context_types.Context, key: uuid.UUID) -> str | None:
    """要求内容の一致を確認して同じ冪等キーの記録済み結果を取得する。"""
    return ctx.idempotent_result(str(key), "submit", request)


def build_submit_version(cached: str) -> models.VersionsRow:
    """後続処理に渡すデータを組み立てる。"""
    return models.VersionsRow.model_validate_json(cached)


def drafts_list(ctx: context_types.Context) -> list[q.DraftsListRow]:
    """現在の組織に属する下書きを識別子順に一覧取得する。"""
    return q.drafts_list(ctx.db, q.DraftsListParams(organization_id=ctx.org))


def validate_draft_revision(row: q.DraftsListRow, data: request_schemas.Submit) -> None:
    """申請元の下書きが読み込み時点から変更されていないことを確認する。"""
    return require(row.revision == data.revision, "conflict", 409)


def assets_get(
    ctx: context_types.Context, placement: shared_schemas.Placement
) -> list[q.AssetsGetRow]:
    """現在の組織に属する指定の添付画像について、画像の保存先・形式・寸法・検証用ハッシュを取得する。"""
    return q.assets_get(ctx.db, q.AssetsGetParams(organization_id=ctx.org, id=placement.asset_id))


def ocr_runs_get(
    ctx: context_types.Context, placement: shared_schemas.Placement
) -> list[q.OcrRunsGetRow]:
    """現在の組織に属する指定の文字認識の実行記録について、認識結果の保存先・検証用ハッシュ・確認状態を取得する。"""
    return q.ocr_runs_get(
        ctx.db, q.OcrRunsGetParams(organization_id=ctx.org, id=placement.ocr_run_id)
    )


def require_confirmed_ocr(ocr: q.OcrRunsGetRow) -> None:
    """添付画像のOCRが確認済みかつ利用可能であることを確認する。"""
    return require(ocr.confirmed and ocr.status == "ready", "ocr_unconfirmed", 409)


def verify_image(asset: q.AssetsGetRow, ctx: context_types.Context) -> bytes:
    """添付画像の実体と記録済みハッシュを照合する。"""
    return ctx.objects.get(asset.object_key, asset.sha256)


def verify_ocr(ocr: q.OcrRunsGetRow, ctx: context_types.Context) -> bytes:
    """確認済みOCRの実体と記録済みハッシュを照合する。"""
    return ctx.objects.get(ocr.result_key, ocr.result_hash)


def verify_body(row: q.DraftsListRow, ctx: context_types.Context) -> bytes:
    """申請する本文の実体と記録済みハッシュを照合する。"""
    return ctx.objects.get(row.body_key, row.body_hash)


def build_version(
    manifest: str, ctx: context_types.Context, doc: models.DocumentsRow, row: q.DraftsListRow
) -> models.VersionsRow:
    """下書きとmanifestから変更不能な確定版の行を組み立てる。"""
    return models.VersionsRow(
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


def versions_insert(ctx: context_types.Context, version: models.VersionsRow) -> int:
    """現在の組織の文書版を、版番号・本文の保存先・画像構成・検証用ハッシュを指定して登録する。"""
    return q.versions_insert(
        ctx.db, q.VersionsInsertParams.model_validate(version, from_attributes=True)
    )


def submissions_insert(
    ctx: context_types.Context, doc: models.DocumentsRow, version: models.VersionsRow
) -> int:
    """現在の組織の承認申請を、対象の文書版・申請者・審査状態・検証用ハッシュとともに登録する。"""
    return q.submissions_insert(
        ctx.db,
        q.SubmissionsInsertParams(
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


def documents_update(ctx: context_types.Context, doc: models.DocumentsRow) -> int:
    """現在の組織に属する指定の文書について、文書の所有部署・公開範囲・状態・公開版の参照を更新する。"""
    return q.documents_update(
        ctx.db,
        q.DocumentsUpdateParams.model_validate(
            doc.model_copy(
                update={
                    "next_version": doc.next_version + 1,
                    "revision": doc.revision + 1,
                    "updated_at": now(),
                }
            ),
            from_attributes=True,
        ),
    )


def record_submit_version_audit(
    ctx: context_types.Context, doc: models.DocumentsRow, version: models.VersionsRow
) -> None:
    """実行した変更の対象と結果を監査記録へ追加する。"""
    return ctx.audit("submit", doc.id, version.id, "draft", "pending")


def remember_submit_version_result(
    request: str, ctx: context_types.Context, key: uuid.UUID, version: models.VersionsRow
) -> None:
    """同じ要求を安全に再試行できるよう冪等キーと結果を記録する。"""
    return ctx.remember(str(key), "submit", request, version.model_dump_json())


def check_concurrent_access(ctx: context_types.Context) -> None:
    """組織の更新競合を検出するための書込みフェンスを更新する。"""
    return ctx.fence()


def read_placements(row: models.DraftsRow) -> list[Placement]:
    """下書きに保存された画像配置を検証済みの配置値へ変換する。"""
    return [Placement.model_validate(value) for value in json.loads(row.placements)]


def build_manifest_image(placement: Placement, image_hash: str, ocr_hash: str) -> ManifestImage:
    """画像配置と確認済みの画像・OCRハッシュを一つのmanifest要素にする。"""
    return ManifestImage(placement=placement, image_hash=image_hash, ocr_hash=ocr_hash)


def serialize_manifest(body_hash: str, images: list[ManifestImage]) -> str:
    """確定する本文と画像構成をmanifestのJSONへ変換する。"""
    return Manifest(body_hash=body_hash, images=images).model_dump_json()
