"""「画像を添付して位置付きOCRを実行」APIの識別子・HTTP境界・認証方式を宣言する。"""

from kotorelay.api_contract import ApiContract

CONTRACT = ApiContract(
    operation_id="upload_image",
    group="images",
    method="POST",
    path="/api/images/documents/{document_id}",
    summary="画像を添付して位置付きOCRを実行",
    auth_mode="bearer",
)
