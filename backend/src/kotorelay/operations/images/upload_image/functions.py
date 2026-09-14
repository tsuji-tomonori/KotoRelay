"""imagesのupload_imageの業務判定と処理を実行する。"""

from __future__ import annotations

import csv
import io
import subprocess
import tempfile
import uuid
from pathlib import Path

from PIL import Image, ImageOps, UnidentifiedImageError

import kotorelay.context as context_types
import kotorelay.generated.models as models
import kotorelay.operations.images.upload_image.generated.queries as q
import kotorelay.schemas as shared_schemas
from kotorelay.context import new_id, now
from kotorelay.errors import Problem, require
from kotorelay.operational_logging import MessageId, continuation_context, ops_logger
from kotorelay.schemas import OcrResult, Region


def normalize_image(data: bytes, max_bytes: int, max_pixels: int) -> tuple[bytes, int, int]:
    """入力画像の形式と寸法を検証し、安全なPNGへ正規化する。"""
    require(0 < len(data) <= max_bytes, "invalid_image", 422)
    try:
        with Image.open(io.BytesIO(data)) as source:
            require(
                source.format in {"PNG", "JPEG"}
                and source.width * source.height <= max_pixels
                and (max(source.width, source.height) <= 8000),
                "invalid_image",
                422,
            )
            source.verify()
        with Image.open(io.BytesIO(data)) as source:
            image = ImageOps.exif_transpose(source).convert("RGB")
            output = io.BytesIO()
            image.save(output, format="PNG")
            value = output.getvalue()
            require(len(value) <= max_bytes, "invalid_image", 422)
            return (value, image.width, image.height)
    except (UnidentifiedImageError, OSError, Image.DecompressionBombError) as exc:
        raise Problem(422, "invalid_image", "画像を読み取れません。") from exc


def run_ocr(data: bytes, width: int, height: int, command: str) -> OcrResult:
    """OCR providerを呼び出して領域とconfidenceを正規化する。"""
    with tempfile.TemporaryDirectory(prefix="kotorelay-ocr-") as folder:
        path = Path(folder) / "image.png"
        path.write_bytes(data)
        try:
            result = subprocess.run(  # noqa: S603 - 管理者設定の実行ファイルをshellなしで呼ぶ。
                [command, str(path), "stdout", "-l", "jpn+eng", "tsv"],
                capture_output=True,
                timeout=30,
                check=True,
            )
        except (OSError, subprocess.TimeoutExpired, subprocess.CalledProcessError) as exc:
            ops_logger.error(
                MessageId.OCR_FAILED, context_model=continuation_context(MessageId.OCR_FAILED, exc)
            )
            return OcrResult(regions=[], engine="tesseract-jpn-eng-v1", status="failed")
        regions: list[Region] = []
        for line in csv.DictReader(io.StringIO(result.stdout.decode()), delimiter="\t"):
            text = line.get("text", "").strip()
            if text:
                regions.append(
                    Region(
                        region_id=new_id(),
                        text=text,
                        x=int(line["left"]) / width,
                        y=int(line["top"]) / height,
                        width=int(line["width"]) / width,
                        height=int(line["height"]) / height,
                        confidence=max(0, min(1, float(line["conf"]) / 100)),
                        order=len(regions),
                    )
                )
        return OcrResult(regions=regions, engine="tesseract-jpn-eng-v1", status="ready")


def document_doc(ctx: context_types.Context, document_id: uuid.UUID) -> models.DocumentsRow:
    """文書を取得して要求された操作の権限を確認する。"""
    return ctx.document(str(document_id), "author")


def select_assets(ctx: context_types.Context, doc: models.DocumentsRow) -> list[q.AssetsListRow]:
    """用途と対象に一致するデータだけを取り出す。"""
    return [
        a
        for a in q.assets_list(ctx.db, q.AssetsListParams(organization_id=ctx.org))
        if a.document_id == doc.id
    ]


def enforce_attachment_limit(assets: list[q.AssetsListRow], ctx: context_types.Context) -> None:
    """文書へ追加できる画像枚数の上限を確認する。"""
    return require(len(assets) < ctx.settings.max_document_images, "limit", 422)


def put_key(value: bytes, ctx: context_types.Context) -> str:
    """本文または画像の実体を保存して内容ハッシュのキーを取得する。"""
    return ctx.objects.put(value, "image/png")


def build_asset(
    key: str,
    width: int,
    height: int,
    ctx: context_types.Context,
    doc: models.DocumentsRow,
    value: bytes,
) -> models.AssetsRow:
    """後続処理に渡すデータを組み立てる。"""
    return models.AssetsRow(
        id=new_id(),
        organization_id=ctx.org,
        document_id=doc.id,
        object_key=key,
        sha256=key,
        media_type="image/png",
        width=width,
        height=height,
        size=len(value),
        created_at=now(),
    )


def assets_insert(ctx: context_types.Context, asset: models.AssetsRow) -> int:
    """現在の組織の文書に添付した画像の保存先・形式・寸法・検証用ハッシュを登録する。"""
    return q.assets_insert(ctx.db, q.AssetsInsertParams.model_validate(asset, from_attributes=True))


def put_result_key(ctx: context_types.Context, result: shared_schemas.OcrResult) -> str:
    """本文または画像の実体を保存して内容ハッシュのキーを取得する。"""
    return ctx.objects.put(result.model_dump_json().encode(), "application/json")


def build_run(
    result_key: str,
    ctx: context_types.Context,
    doc: models.DocumentsRow,
    asset: models.AssetsRow,
    result: shared_schemas.OcrResult,
) -> models.OcrRunsRow:
    """後続処理に渡すデータを組み立てる。"""
    return models.OcrRunsRow(
        id=new_id(),
        organization_id=ctx.org,
        document_id=doc.id,
        asset_id=asset.id,
        result_key=result_key,
        result_hash=result_key,
        engine=result.engine,
        status=result.status,
        confirmed=False,
        created_at=now(),
    )


def ocr_runs_insert(ctx: context_types.Context, run: models.OcrRunsRow) -> int:
    """現在の組織の画像に対する文字認識の実行記録を、認識結果の保存先・検証用ハッシュ・確認状態とともに登録する。"""
    return q.ocr_runs_insert(
        ctx.db, q.OcrRunsInsertParams.model_validate(run, from_attributes=True)
    )


def check_concurrent_access(ctx: context_types.Context) -> None:
    """組織の更新競合を検出するための書込みフェンスを更新する。"""
    return ctx.fence()


def build_upload_image(
    asset: models.AssetsRow, run: models.OcrRunsRow, result: shared_schemas.OcrResult
) -> dict[str, object]:
    """後続処理に渡すデータを組み立てる。"""
    return {"asset": asset, "ocr_run": run, "ocr": result}
