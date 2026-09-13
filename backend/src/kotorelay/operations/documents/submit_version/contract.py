"""「版を確定して承認申請」APIの識別子・HTTP境界・認証方式を宣言する。"""

from kotorelay.api_contract import ApiContract

CONTRACT = ApiContract(
    operation_id="submit_version",
    group="documents",
    method="POST",
    path="/api/documents/{document_id}/submissions",
    summary="版を確定して承認申請",
    auth_mode="bearer",
)
