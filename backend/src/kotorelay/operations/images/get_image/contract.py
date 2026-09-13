"""「現在の認可で画像を配信」APIの識別子・HTTP境界・認証方式を宣言する。"""

from kotorelay.api_contract import ApiContract

CONTRACT = ApiContract(
    operation_id="get_image",
    group="images",
    method="GET",
    path="/api/images/{asset_id}",
    summary="現在の認可で画像を配信",
    auth_mode="bearer",
)
