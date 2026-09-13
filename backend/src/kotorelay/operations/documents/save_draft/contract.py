"""「競合を検出して下書きを保存」APIの識別子・HTTP境界・認証方式を宣言する。"""

from kotorelay.api_contract import ApiContract

CONTRACT = ApiContract(
    operation_id="save_draft",
    group="documents",
    method="PUT",
    path="/api/documents/{document_id}/draft",
    summary="競合を検出して下書きを保存",
    auth_mode="bearer",
)
