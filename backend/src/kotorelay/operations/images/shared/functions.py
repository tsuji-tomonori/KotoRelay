"""imagesのsharedの業務判定と処理を実行する。"""

from __future__ import annotations

from kotorelay.context import Context
from kotorelay.errors import require
from kotorelay.generated import models
from kotorelay.operations.images.shared.generated import queries as q
from kotorelay.schemas import Manifest


def authorize_asset(ctx: Context, asset_id: str, version_id: str | None) -> models.AssetsRow:
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
