"""「反映ジョブを再処理」APIの識別子・HTTP境界・認証方式を宣言する。"""

from kotorelay.api_contract import ApiContract

CONTRACT = ApiContract(
    operation_id="retry_job",
    group="indexing",
    method="POST",
    path="/api/operations/jobs/{job_id}",
    summary="反映ジョブを再処理",
    auth_mode="bearer",
)
