"""imagesのupload_imageの業務判定と処理を実行する。"""

from __future__ import annotations

import csv
import io
import subprocess
import tempfile
from pathlib import Path

from PIL import Image, ImageOps, UnidentifiedImageError

from kotorelay.context import Context, new_id, now
from kotorelay.errors import Problem, require
from kotorelay.generated import models
from kotorelay.operations.images.upload_image.generated import queries as q
from kotorelay.schemas import OcrResult, Region


def upload(ctx: Context, document_id: str, data: bytes) -> dict[str, object]:
    doc = ctx.document(document_id, "author")
    assets = [a for a in q.assets_list(ctx.db, ctx.org) if a.document_id == doc.id]
    require(len(assets) < ctx.settings.max_document_images, "limit", 422)
    value, width, height = normalize_image(
        data, ctx.settings.max_image_bytes, ctx.settings.max_image_pixels
    )
    key = ctx.objects.put(value, "image/png")
    asset = models.AssetsRow(
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
    q.assets_insert(ctx.db, asset)
    result = run_ocr(value, width, height, ctx.settings.ocr_command)
    result_key = ctx.objects.put(result.model_dump_json().encode(), "application/json")
    run = models.OcrRunsRow(
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
    q.ocr_runs_insert(ctx.db, run)
    ctx.fence()
    return {"asset": asset, "ocr_run": run, "ocr": result}


def normalize_image(data: bytes, max_bytes: int, max_pixels: int) -> tuple[bytes, int, int]:
    require(0 < len(data) <= max_bytes, "invalid_image", 422)
    try:
        with Image.open(io.BytesIO(data)) as source:
            require(
                source.format in {"PNG", "JPEG"}
                and source.width * source.height <= max_pixels
                and max(source.width, source.height) <= 8000,
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
            return value, image.width, image.height
    except (UnidentifiedImageError, OSError, Image.DecompressionBombError) as exc:
        raise Problem(422, "invalid_image", "画像を読み取れません。") from exc


def run_ocr(data: bytes, width: int, height: int, command: str) -> OcrResult:
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
        except (OSError, subprocess.TimeoutExpired, subprocess.CalledProcessError):
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
