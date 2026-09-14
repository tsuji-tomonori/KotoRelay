"""imagesのcorrect_ocrの業務判定と処理を実行する。"""

from __future__ import annotations

import uuid

import kotorelay.context as context_types
import kotorelay.generated.models as models
import kotorelay.operations.images.correct_ocr.generated.queries as q
import kotorelay.operations.images.correct_ocr.schemas as request_schemas
import kotorelay.schemas as shared_schemas
from kotorelay.context import new_id, now
from kotorelay.errors import require


def assets_get(ctx: context_types.Context, asset_id: uuid.UUID) -> list[q.AssetsGetRow]:
    """現在の組織に属する指定の添付画像について、画像の保存先・形式・寸法・検証用ハッシュを取得する。"""
    return q.assets_get(ctx.db, q.AssetsGetParams(organization_id=ctx.org, id=str(asset_id)))


def require_asset(assets: list[q.AssetsGetRow]) -> None:
    """補正対象の添付画像が存在することを確認する。"""
    return require(bool(assets))


def require_document_author(ctx: context_types.Context, asset: q.AssetsGetRow) -> None:
    """文書を取得して要求された操作の権限を確認する。"""
    ctx.document(asset.document_id, "author")


def select_ids(data: request_schemas.OcrCorrection) -> list[str]:
    """用途と対象に一致するデータだけを取り出す。"""
    return [r.region_id for r in data.regions if r.region_id is not None]


def validate_region_ids(ids: list[str]) -> None:
    """OCR領域の識別子に重複がないことを確認する。"""
    return require(len(ids) == len(set(ids)), "invalid_region", 422)


def validate_region_bounds(region: shared_schemas.Region) -> None:
    """OCR領域が画像の正規化座標の範囲内に収まることを確認する。"""
    return require(
        region.x + region.width <= 1.000001 and region.y + region.height <= 1.000001,
        "invalid_region",
        422,
    )


def select_result(data: request_schemas.OcrCorrection) -> list[shared_schemas.Region]:
    """用途と対象に一致するデータだけを取り出す。"""
    return [
        r.model_copy(
            update={"region_id": r.region_id or new_id(), "source": "human", "confidence": None}
        )
        for r in data.regions
    ]


def put_key(ctx: context_types.Context, result: shared_schemas.OcrResult) -> str:
    """本文または画像の実体を保存して内容ハッシュのキーを取得する。"""
    return ctx.objects.put(result.model_dump_json().encode(), "application/json")


def build_run(
    key: str,
    ctx: context_types.Context,
    asset: q.AssetsGetRow,
    result: shared_schemas.OcrResult,
    data: request_schemas.OcrCorrection,
) -> models.OcrRunsRow:
    """後続処理に渡すデータを組み立てる。"""
    return models.OcrRunsRow(
        id=new_id(),
        organization_id=ctx.org,
        document_id=asset.document_id,
        asset_id=asset.id,
        result_key=key,
        result_hash=key,
        engine=result.engine,
        status="ready",
        confirmed=data.confirmed,
        created_at=now(),
    )


def ocr_runs_insert(ctx: context_types.Context, run: models.OcrRunsRow) -> int:
    """現在の組織の画像に対する文字認識の実行記録を、認識結果の保存先・検証用ハッシュ・確認状態とともに登録する。"""
    return q.ocr_runs_insert(
        ctx.db, q.OcrRunsInsertParams.model_validate(run, from_attributes=True)
    )


def record_correct_ocr_audit(ctx: context_types.Context, asset: q.AssetsGetRow) -> None:
    """実行した変更の対象と結果を監査記録へ追加する。"""
    return ctx.audit("ocr_correction", asset.document_id)


def check_concurrent_access(ctx: context_types.Context) -> None:
    """組織の更新競合を検出するための書込みフェンスを更新する。"""
    return ctx.fence()


def build_correct_ocr(
    run: models.OcrRunsRow, result: shared_schemas.OcrResult
) -> dict[str, object]:
    """後続処理に渡すデータを組み立てる。"""
    return {"ocr_run": run, "ocr": result}
