"""「本人と現在の所属権限を取得」APIの識別子・HTTP境界・認証方式を宣言する。"""

from kotorelay.api_contract import ApiContract

CONTRACT = ApiContract(
    operation_id="get_identity",
    group="groups",
    method="GET",
    path="/api/groups/me",
    summary="本人と現在の所属権限を取得",
    auth_mode="bearer",
)
