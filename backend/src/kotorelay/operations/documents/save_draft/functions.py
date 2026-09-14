"""documentsのsave_draftの業務判定と処理を実行する。"""

from __future__ import annotations

import json
import uuid

import kotorelay.context as context_types
import kotorelay.generated.models as models
import kotorelay.operations.documents.save_draft.generated.queries as q
import kotorelay.operations.documents.save_draft.schemas as request_schemas
from kotorelay.context import Context, now
from kotorelay.errors import require
from kotorelay.operations.documents.save_draft.schemas import SaveDraft


def validate_placements(ctx: Context, doc: models.DocumentsRow, data: SaveDraft) -> None:
    """本文内の画像配置と添付画像・OCRの所有先と有効性を照合する。"""
    require(len({p.id for p in data.placements}) == len(data.placements), "invalid_placement", 422)
    for placement in data.placements:
        assets = q.assets_get(
            ctx.db, q.AssetsGetParams(organization_id=ctx.org, id=placement.asset_id)
        )
        runs = q.ocr_runs_get(
            ctx.db, q.OcrRunsGetParams(organization_id=ctx.org, id=placement.ocr_run_id)
        )
        require(bool(assets) and bool(runs), "invalid_placement", 422)
        require(
            assets[0].document_id == doc.id
            and runs[0].asset_id == assets[0].id
            and (runs[0].document_id == doc.id)
            and (placement.offset <= len(data.body)),
            "invalid_placement",
            422,
        )


def document_doc(ctx: context_types.Context, document_id: uuid.UUID) -> models.DocumentsRow:
    """文書を取得して要求された操作の権限を確認する。"""
    return ctx.document(str(document_id), "author")


def drafts_list(ctx: context_types.Context) -> list[q.DraftsListRow]:
    """現在の組織に属する下書きを識別子順に一覧取得する。"""
    return q.drafts_list(ctx.db, q.DraftsListParams(organization_id=ctx.org))


def validate_draft_revision(row: q.DraftsListRow, data: request_schemas.SaveDraft) -> None:
    """下書きが読み込み時点から変更されていないことを確認する。"""
    return require(row.revision == data.revision, "conflict", 409)


def put_key(ctx: context_types.Context, data: request_schemas.SaveDraft) -> str:
    """本文または画像の実体を保存して内容ハッシュのキーを取得する。"""
    return ctx.objects.put(data.body.encode(), "text/markdown")


def drafts_update(
    ctx: context_types.Context, row: q.DraftsListRow, key: str, data: request_schemas.SaveDraft
) -> int:
    """現在の組織に属する指定の下書きについて、本文の保存先・画像配置・改訂番号を更新する。"""
    return q.drafts_update(
        ctx.db,
        q.DraftsUpdateParams.model_validate(
            row.model_copy(
                update={
                    "body_key": key,
                    "body_hash": key,
                    "revision": row.revision + 1,
                    "updated_by": ctx.user.id,
                    "placements": json.dumps([p.model_dump() for p in data.placements]),
                }
            ),
            from_attributes=True,
        ),
    )


def documents_update(
    ctx: context_types.Context, doc: models.DocumentsRow, data: request_schemas.SaveDraft
) -> int:
    """現在の組織に属する指定の文書について、文書の所有部署・公開範囲・状態・公開版の参照を更新する。"""
    return q.documents_update(
        ctx.db,
        q.DocumentsUpdateParams.model_validate(
            doc.model_copy(
                update={"title": data.title, "revision": doc.revision + 1, "updated_at": now()}
            ),
            from_attributes=True,
        ),
    )


def check_concurrent_access(ctx: context_types.Context) -> None:
    """組織の更新競合を検出するための書込みフェンスを更新する。"""
    return ctx.fence()


def is_document_draft(row: q.DraftsListRow, document_id: str) -> bool:
    """下書きが保存対象の文書に属している。"""
    return row.document_id == document_id
