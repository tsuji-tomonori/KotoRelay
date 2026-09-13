"""imagesのcorrect_ocrの業務判定と処理を実行する。"""

from __future__ import annotations

from kotorelay.context import Context, new_id, now
from kotorelay.errors import require
from kotorelay.generated import models
from kotorelay.operations.images.correct_ocr.generated import queries as q
from kotorelay.operations.images.correct_ocr.schemas import OcrCorrection
from kotorelay.schemas import OcrResult


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
    run = models.OcrRunsRow(
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
