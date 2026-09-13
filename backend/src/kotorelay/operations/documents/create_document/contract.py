"""「文書を作成」APIの識別子・HTTP境界・認証方式を宣言する。"""

from kotorelay.api_contract import ApiContract

CONTRACT = ApiContract(
    operation_id="create_document",
    group="documents",
    method="POST",
    path="/api/documents",
    summary="文書を作成",
    auth_mode="bearer",
)
