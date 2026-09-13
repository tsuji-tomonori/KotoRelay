"""「リーダーが公開範囲・公開停止・削除を管理」APIの識別子・HTTP境界・認証方式を宣言する。"""

from kotorelay.api_contract import ApiContract

CONTRACT = ApiContract(
    operation_id="change_policy",
    group="documents",
    method="PUT",
    path="/api/documents/{document_id}/policy",
    summary="リーダーが公開範囲・公開停止・削除を管理",
    auth_mode="bearer",
)
