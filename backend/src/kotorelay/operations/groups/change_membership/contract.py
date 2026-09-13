"""「部署の所属権限を変更」APIの識別子・HTTP境界・認証方式を宣言する。"""

from kotorelay.api_contract import ApiContract

CONTRACT = ApiContract(
    operation_id="change_membership",
    group="groups",
    method="PUT",
    path="/api/groups/memberships",
    summary="部署の所属権限を変更",
    auth_mode="bearer",
)
