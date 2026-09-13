"""「審査状況を一覧」APIの識別子・HTTP境界・認証方式を宣言する。"""

from kotorelay.api_contract import ApiContract

CONTRACT = ApiContract(
    operation_id="list_reviews",
    group="reviews",
    method="GET",
    path="/api/reviews",
    summary="審査状況を一覧",
    auth_mode="bearer",
)
