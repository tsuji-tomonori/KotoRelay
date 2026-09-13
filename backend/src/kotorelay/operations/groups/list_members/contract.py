"""「自部署の所属を一覧」APIの識別子・HTTP境界・認証方式を宣言する。"""

from kotorelay.api_contract import ApiContract

CONTRACT = ApiContract(
    operation_id="list_members",
    group="groups",
    method="GET",
    path="/api/groups/{department_id}/members",
    summary="自部署の所属を一覧",
    auth_mode="bearer",
)
