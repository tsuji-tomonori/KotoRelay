"""「実閲覧を一意IDで記録」APIの識別子・HTTP境界・認証方式を宣言する。"""

from kotorelay.api_contract import ApiContract

CONTRACT = ApiContract(
    operation_id="record_view",
    group="metrics",
    method="POST",
    path="/api/metrics/views/{document_id}",
    summary="実閲覧を一意IDで記録",
    auth_mode="bearer",
)
