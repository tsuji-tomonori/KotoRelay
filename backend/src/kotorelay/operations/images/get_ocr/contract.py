"""「認可されたOCR領域を取得」APIの識別子・HTTP境界・認証方式を宣言する。"""

from kotorelay.api_contract import ApiContract

CONTRACT = ApiContract(
    operation_id="get_ocr",
    group="images",
    method="GET",
    path="/api/images/ocr/{run_id}",
    summary="認可されたOCR領域を取得",
    auth_mode="bearer",
)
