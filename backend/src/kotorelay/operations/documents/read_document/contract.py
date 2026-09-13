"""「承認版または担当版を表示」APIの識別子・HTTP境界・認証方式を宣言する。"""

from kotorelay.api_contract import ApiContract

CONTRACT = ApiContract(
    operation_id="read_document",
    group="documents",
    method="GET",
    path="/api/documents/{document_id}",
    summary="承認版または担当版を表示",
    auth_mode="bearer",
)
