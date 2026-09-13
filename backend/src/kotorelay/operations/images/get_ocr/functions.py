"""imagesのget_ocrの業務判定と処理を実行する。"""

from __future__ import annotations

from kotorelay.context import Context, stable_id
from kotorelay.errors import require
from kotorelay.operations.images.get_ocr.generated import queries as q
from kotorelay.operations.images.shared.functions import authorize_asset
from kotorelay.schemas import Manifest, OcrResult


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
