"""画像を正規化し、位置付きOCRと人の訂正を不変のrunとして保存する。"""

from __future__ import annotations

import csv
import io
import subprocess
import tempfile
from pathlib import Path

from PIL import Image, ImageOps, UnidentifiedImageError

from kotorelay.context import Context, new_id, now, stable_id
from kotorelay.errors import Problem, require
from kotorelay.generated import queries as q
from kotorelay.schemas import Manifest, OcrCorrection, OcrResult, Region


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


def upload(ctx: Context, document_id: str, data: bytes) -> dict[str, object]:
    doc = ctx.document(document_id, "author")
    assets = [a for a in q.assets_list(ctx.db, ctx.org) if a.document_id == doc.id]
    require(len(assets) < ctx.settings.max_document_images, "limit", 422)
    value, width, height = normalize_image(
        data, ctx.settings.max_image_bytes, ctx.settings.max_image_pixels
    )
    key = ctx.objects.put(value, "image/png")
    asset = q.AssetsRow(
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
    run = q.OcrRunsRow(
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


def correct(ctx: Context, asset_id: str, data: OcrCorrection) -> dict[str, object]:
    assets = q.assets_get(ctx.db, ctx.org, asset_id)
    require(bool(assets))
    asset = assets[0]
    ctx.document(asset.document_id, "author")
    ids = [r.region_id for r in data.regions if r.region_id is not None]
    require(len(ids) == len(set(ids)), "invalid_region", 422)
    for region in data.regions:
        require(
            region.x + region.width <= 1.000001 and region.y + region.height <= 1.000001,
            "invalid_region",
            422,
        )
    result = OcrResult(
        regions=[
            r.model_copy(
                update={"region_id": r.region_id or new_id(), "source": "human", "confidence": None}
            )
            for r in data.regions
        ],
        engine="human-correction-v1",
        status="ready",
        confirmed=data.confirmed,
    )
    key = ctx.objects.put(result.model_dump_json().encode(), "application/json")
    run = q.OcrRunsRow(
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
    q.ocr_runs_insert(ctx.db, run)
    ctx.audit("ocr_correction", asset.document_id)
    ctx.fence()
    return {"ocr_run": run, "ocr": result}


def authorize_asset(ctx: Context, asset_id: str, version_id: str | None) -> q.AssetsRow:
    assets = q.assets_get(ctx.db, ctx.org, asset_id)
    require(bool(assets))
    asset = assets[0]
    if version_id is None:
        ctx.document(asset.document_id, "draft")
    else:
        docs = q.documents_get(ctx.db, ctx.org, asset.document_id)
        require(bool(docs) and docs[0].status != "deleted")
        doc = docs[0]
        require(ctx.can_read(doc) or ctx.permission(doc.department_id, "draft"))
        version = ctx.version(doc, version_id)
        manifest = Manifest.model_validate_json(version.manifest)
        require(
            any(
                i.placement.asset_id == asset.id and i.image_hash == asset.sha256
                for i in manifest.images
            )
        )
    return asset


def image(ctx: Context, asset_id: str, version_id: str | None) -> bytes:
    asset = authorize_asset(ctx, asset_id, version_id)
    return ctx.objects.get(asset.object_key, asset.sha256)


def ocr(ctx: Context, run_id: str, version_id: str | None) -> OcrResult:
    rows = q.ocr_runs_get(ctx.db, ctx.org, run_id)
    require(bool(rows))
    run = rows[0]
    asset = authorize_asset(ctx, run.asset_id, version_id)
    if version_id:
        doc = q.documents_get(ctx.db, ctx.org, asset.document_id)[0]
        version = ctx.version(doc, version_id)
        require(
            any(
                i.placement.ocr_run_id == run.id and i.ocr_hash == run.result_hash
                for i in Manifest.model_validate_json(version.manifest).images
            )
        )
    result = OcrResult.model_validate_json(ctx.objects.get(run.result_key, run.result_hash))
    # 旧runは読取時だけ安定IDを補い、承認済みのJSONとハッシュを変更しない。
    return result.model_copy(
        update={
            "confirmed": run.confirmed,
            "regions": [
                r.model_copy(update={"region_id": r.region_id or stable_id(run.id + ":" + str(i))})
                for i, r in enumerate(result.regions)
            ],
        }
    )
