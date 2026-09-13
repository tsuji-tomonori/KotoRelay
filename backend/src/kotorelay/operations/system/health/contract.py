"""「死活確認」APIの識別子・HTTP境界・認証方式を宣言する。"""

from kotorelay.api_contract import ApiContract

CONTRACT = ApiContract(
    operation_id="health",
    group="system",
    method="GET",
    path="/api/health",
    summary="死活確認",
    auth_mode="public",
)
