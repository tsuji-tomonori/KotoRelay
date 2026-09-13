"""「閲覧可能な文書を検索」APIの識別子・HTTP境界・認証方式を宣言する。"""

from kotorelay.api_contract import ApiContract

CONTRACT = ApiContract(
    operation_id="list_documents",
    group="documents",
    method="GET",
    path="/api/documents",
    summary="閲覧可能な文書を検索",
    auth_mode="bearer",
)
