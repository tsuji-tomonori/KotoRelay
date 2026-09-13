"""「manifestを確認して承認・却下」APIの識別子・HTTP境界・認証方式を宣言する。"""

from kotorelay.api_contract import ApiContract

CONTRACT = ApiContract(
    operation_id="decide_review",
    group="reviews",
    method="POST",
    path="/api/reviews/{submission_id}/decision",
    summary="manifestを確認して承認・却下",
    auth_mode="bearer",
)
