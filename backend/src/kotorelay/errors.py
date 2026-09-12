"""機密情報を含めない業務エラーを定義する。"""


class Problem(Exception):
    def __init__(self, status: int, code: str, message: str):
        self.status = status
        self.code = code
        self.message = message
        super().__init__(message)


def require(condition: bool, code: str = "not_found", status: int = 404) -> None:
    if not condition:
        raise Problem(status, code, MESSAGES.get(code, "対象を利用できません。"))


MESSAGES = {
    "not_found": "対象を利用できません。",
    "unauthenticated": "ログインが必要です。",
    "forbidden": "この操作は許可されていません。",
    "conflict": "他の操作で更新されました。最新の状態を確認してください。",
    "self_approval": "自分が作成した版は承認できません。",
    "ocr_unconfirmed": "すべての画像のOCRを確認してください。",
    "invalid_image": "PNG/JPEGの許可サイズ内の画像を指定してください。",
    "invalid_placement": "画像の配置またはOCR参照が無効です。",
    "integrity": "保存内容の整合性を確認できません。",
    "limit": "利用上限に達しました。",
    "idempotency_conflict": "同じ操作IDが異なる内容で使用されています。",
}
