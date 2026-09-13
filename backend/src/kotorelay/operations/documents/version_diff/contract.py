"""「版IDを指定して本文差分を比較」APIの識別子・HTTP境界・認証方式を宣言する。"""

from kotorelay.api_contract import ApiContract

CONTRACT = ApiContract(
    operation_id="version_diff",
    group="documents",
    method="GET",
    path="/api/documents/{document_id}/diff",
    summary="版IDを指定して本文差分を比較",
    auth_mode="bearer",
)
