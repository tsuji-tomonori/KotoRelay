"""imagesのget_imageの業務判定と処理を実行する。"""

from __future__ import annotations

import kotorelay.context as context_types
import kotorelay.generated.models as models


def get_get_image(asset: models.AssetsRow, ctx: context_types.Context) -> bytes:
    """記録された保存先から実体を取得してハッシュを照合する。"""
    return ctx.objects.get(asset.object_key, asset.sha256)
