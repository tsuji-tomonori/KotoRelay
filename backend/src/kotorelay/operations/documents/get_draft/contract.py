"""「下書きを取得」APIの識別子・HTTP境界・認証方式を宣言する。"""

from kotorelay.api_contract import ApiContract

CONTRACT = ApiContract(
    operation_id="get_draft",
    group="documents",
    method="GET",
    path="/api/documents/{document_id}/draft",
    summary="下書きを取得",
    auth_mode="bearer",
)
