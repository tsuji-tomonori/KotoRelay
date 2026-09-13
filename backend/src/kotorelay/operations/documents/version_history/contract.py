"""「担当文書の版履歴」APIの識別子・HTTP境界・認証方式を宣言する。"""

from kotorelay.api_contract import ApiContract

CONTRACT = ApiContract(
    operation_id="version_history",
    group="documents",
    method="GET",
    path="/api/documents/{document_id}/history",
    summary="担当文書の版履歴",
    auth_mode="bearer",
)
