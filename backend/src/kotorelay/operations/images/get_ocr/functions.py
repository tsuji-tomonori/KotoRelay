"""imagesのget_ocrの業務判定と処理を実行する。"""

from __future__ import annotations

import uuid

import kotorelay.context as context_types
import kotorelay.generated.models as models
import kotorelay.operations.images.get_ocr.generated.queries as q
import kotorelay.schemas as shared_schemas
from kotorelay.context import stable_id
from kotorelay.errors import require
from kotorelay.schemas import Manifest, OcrResult


def ocr_runs_get(ctx: context_types.Context, run_id: uuid.UUID) -> list[q.OcrRunsGetRow]:
    """現在の組織に属する指定の文字認識の実行記録について、認識結果の保存先・検証用ハッシュ・確認状態を取得する。"""
    return q.ocr_runs_get(ctx.db, q.OcrRunsGetParams(organization_id=ctx.org, id=str(run_id)))


def require_ocr_run(rows: list[q.OcrRunsGetRow]) -> None:
    """OCR実行記録が存在することを確認する。"""
    return require(bool(rows))


def documents_get(ctx: context_types.Context, asset: models.AssetsRow) -> list[q.DocumentsGetRow]:
    """現在の組織に属する指定の文書について、文書の所有部署・公開範囲・状態・公開版の参照を取得する。"""
    return q.documents_get(
        ctx.db, q.DocumentsGetParams(organization_id=ctx.org, id=asset.document_id)
    )


def version_version(
    doc: q.DocumentsGetRow, ctx: context_types.Context, version_id: uuid.UUID
) -> models.VersionsRow:
    """対象文書に属する確定版を取得する。"""
    return ctx.version(doc, str(version_id))


def validate_version_ocr(run: q.OcrRunsGetRow, version: models.VersionsRow) -> None:
    """指定版のmanifestに同じOCR実行とハッシュが含まれることを確認する。"""
    return require(
        any(
            i.placement.ocr_run_id == run.id and i.ocr_hash == run.result_hash
            for i in Manifest.model_validate_json(version.manifest).images
        )
    )


def build_result(run: q.OcrRunsGetRow, ctx: context_types.Context) -> shared_schemas.OcrResult:
    """後続処理に渡すデータを組み立てる。"""
    return OcrResult.model_validate_json(ctx.objects.get(run.result_key, run.result_hash))


def build_get_ocr(
    result: shared_schemas.OcrResult, run: q.OcrRunsGetRow
) -> shared_schemas.OcrResult:
    """後続処理に渡すデータを組み立てる。"""
    return result.model_copy(
        update={
            "confirmed": run.confirmed,
            "regions": [
                r.model_copy(update={"region_id": r.region_id or stable_id(run.id + ":" + str(i))})
                for i, r in enumerate(result.regions)
            ],
        }
    )
