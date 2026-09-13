"""「最新承認版の根拠で回答」APIの識別子・HTTP境界・認証方式を宣言する。"""

from kotorelay.api_contract import ApiContract

CONTRACT = ApiContract(
    operation_id="ask_question",
    group="chat",
    method="POST",
    path="/api/chat",
    summary="最新承認版の根拠で回答",
    auth_mode="bearer",
)
