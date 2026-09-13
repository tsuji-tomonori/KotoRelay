"""「正本と索引の不一致を確認」APIの識別子・HTTP境界・認証方式を宣言する。"""

from kotorelay.api_contract import ApiContract

CONTRACT = ApiContract(
    operation_id="reconcile_index",
    group="indexing",
    method="GET",
    path="/api/operations/reconcile",
    summary="正本と索引の不一致を確認",
    auth_mode="bearer",
)
