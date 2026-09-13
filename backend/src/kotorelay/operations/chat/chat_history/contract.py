"""「現行認可で会話履歴を再表示」APIの識別子・HTTP境界・認証方式を宣言する。"""

from kotorelay.api_contract import ApiContract

CONTRACT = ApiContract(
    operation_id="chat_history",
    group="chat",
    method="GET",
    path="/api/chat/{conversation_id}",
    summary="現行認可で会話履歴を再表示",
    auth_mode="bearer",
)
