"""「部署の利用数と文書貢献を集計」APIの識別子・HTTP境界・認証方式を宣言する。"""

from kotorelay.api_contract import ApiContract

CONTRACT = ApiContract(
    operation_id="department_metrics",
    group="metrics",
    method="GET",
    path="/api/metrics/{department_id}",
    summary="部署の利用数と文書貢献を集計",
    auth_mode="bearer",
)
