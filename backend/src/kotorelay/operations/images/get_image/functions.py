"""imagesのget_imageの業務判定と処理を実行する。"""

from __future__ import annotations

from kotorelay.context import Context
from kotorelay.operations.images.shared.functions import authorize_asset


def image(ctx: Context, asset_id: str, version_id: str | None) -> bytes:
    asset = authorize_asset(ctx, asset_id, version_id)
    return ctx.objects.get(asset.object_key, asset.sha256)
