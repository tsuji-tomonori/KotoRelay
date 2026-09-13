"""下書きの取得・認可・本文復元・応答組立を個別に提供する。"""

import json

from kotorelay.context import Context
from kotorelay.generated import models
from kotorelay.operations.documents.shared.generated import queries as q


def authorize_draft(ctx: Context, document_id: str) -> models.DocumentsRow:
    """指定文書を取得して下書きの閲覧権限を確認する。"""
    return ctx.document(document_id, "draft")


def load_draft_row(ctx: Context, document_id: str) -> q.DraftsListRow:
    """組織内の下書きから対象文書の現在の改訂を取得する。"""
    return next(
        row
        for row in q.drafts_list(ctx.db, q.DraftsListParams(organization_id=ctx.org))
        if row.document_id == document_id
    )


def load_draft_body(ctx: Context, row: models.DraftsRow) -> str:
    """下書き本文のハッシュを照合してテキストを復元する。"""
    return ctx.objects.get(row.body_key, row.body_hash).decode()


def build_draft_data(
    doc: models.DocumentsRow, row: models.DraftsRow, body: str
) -> dict[str, object]:
    """文書・本文・改訂番号・画像配置を下書きの応答用データにまとめる。"""
    return {
        "document": doc,
        "body": body,
        "revision": row.revision,
        "placements": json.loads(row.placements),
    }
