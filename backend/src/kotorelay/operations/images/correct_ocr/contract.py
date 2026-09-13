"""「OCRを訂正し新しいrunを保存」APIの識別子・HTTP境界・認証方式を宣言する。"""

from kotorelay.api_contract import ApiContract

CONTRACT = ApiContract(
    operation_id="correct_ocr",
    group="images",
    method="POST",
    path="/api/images/{asset_id}/ocr",
    summary="OCRを訂正し新しいrunを保存",
    auth_mode="bearer",
)
