"""imagesのsharedの業務判定と処理を実行する。"""

from __future__ import annotations

from typing import cast

from kotorelay.context import Context
from kotorelay.errors import require
from kotorelay.generated import models
from kotorelay.operations.images.shared.generated import queries as q
from kotorelay.schemas import Manifest


def authorize_asset(ctx: Context, asset_id: str, version_id: str | None) -> models.AssetsRow:
    """画像の所有文書と指定版の閲覧権限を確認して実体情報を返す。"""
    assets = q.assets_get(ctx.db, q.AssetsGetParams(organization_id=ctx.org, id=asset_id))
    require(bool(assets))
    asset = assets[0]
    if has_no_requested_version(version_id):
        ctx.document(asset.document_id, "draft")
    else:
        docs = q.documents_get(
            ctx.db, q.DocumentsGetParams(organization_id=ctx.org, id=asset.document_id)
        )
        require(bool(docs) and docs[0].status != "deleted")
        doc = docs[0]
        require(ctx.can_read(doc) or ctx.permission(doc.department_id, "draft"))
        version = ctx.version(doc, cast(str, version_id))
        manifest = Manifest.model_validate_json(version.manifest)
        require(
            any(
                i.placement.asset_id == asset.id and i.image_hash == asset.sha256
                for i in manifest.images
            )
        )
    return asset


def has_no_requested_version(version_id: str | None) -> bool:
    """版の指定がなく、下書きの画像として権限を確認する。"""
    return version_id is None
