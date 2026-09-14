"""共通認可で使う操作条件を判定する。"""


def is_read_operation(operation: str) -> bool:
    """文書の閲覧権限を確認する操作である。"""
    return operation == "read"
