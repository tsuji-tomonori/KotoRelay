"""「反映ジョブと失敗理由を確認」APIの識別子・HTTP境界・認証方式を宣言する。"""

from kotorelay.api_contract import ApiContract

CONTRACT = ApiContract(
    operation_id="list_jobs",
    group="indexing",
    method="GET",
    path="/api/operations/jobs",
    summary="反映ジョブと失敗理由を確認",
    auth_mode="bearer",
)
