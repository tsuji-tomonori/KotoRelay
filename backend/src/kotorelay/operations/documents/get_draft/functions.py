"""documentsのget_draftの業務判定と処理を実行する。"""

from __future__ import annotations

from kotorelay.context import Context
from kotorelay.operations.documents.shared.functions import draft as load_draft


def draft(ctx: Context, document_id: str) -> dict[str, object]:
    """担当権限を検証して下書きの本文と配置を取得する。"""
    return load_draft(ctx, document_id)
