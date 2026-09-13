"""documentsのcreate_documentの業務判定と処理を実行する。"""

from __future__ import annotations

import kotorelay.context as context_types
import kotorelay.generated.models as models
import kotorelay.operations.documents.create_document.schemas as request_schemas
from kotorelay.context import new_id, now
from kotorelay.errors import require
from kotorelay.operations.documents.create_document.generated import queries as q


def require_author_permission(
    ctx: context_types.Context, data: request_schemas.CreateDocument
) -> None:
    """作成先部署で文書を執筆できる権限を確認する。"""
    return require(ctx.permission(data.department_id, "author"), "forbidden", 403)


def initialize_document(
    ctx: context_types.Context, data: request_schemas.CreateDocument
) -> models.DocumentsRow:
    """部署・所有者・初期公開範囲を指定して文書の初期状態を組み立てる。"""
    return models.DocumentsRow(
        id=new_id(),
        organization_id=ctx.org,
        department_id=data.department_id,
        title=data.title,
        created_by=ctx.user.id,
        visibility="department",
        shared_departments="[]",
        status="active",
        revision=1,
        next_version=1,
        latest_version_id=None,
        updated_at=now(),
    )


def documents_insert(ctx: context_types.Context, doc: models.DocumentsRow) -> int:
    """現在の組織の文書を、所有部署・公開範囲・状態を指定して登録する。"""
    return q.documents_insert(
        ctx.db, q.DocumentsInsertParams.model_validate(doc, from_attributes=True)
    )


def save_empty_body(ctx: context_types.Context) -> str:
    """新規下書きの空の本文実体を保存する。"""
    return ctx.objects.put(b"")


def drafts_insert(ctx: context_types.Context, key: str, doc: models.DocumentsRow) -> int:
    """現在の組織の文書の下書きを、本文の保存先・画像配置・改訂番号を指定して登録する。"""
    return q.drafts_insert(
        ctx.db,
        q.DraftsInsertParams(
            id=new_id(),
            organization_id=ctx.org,
            document_id=doc.id,
            body_key=key,
            body_hash=key,
            placements="[]",
            revision=1,
            updated_by=ctx.user.id,
        ),
    )


def record_create_document_audit(ctx: context_types.Context, doc: models.DocumentsRow) -> None:
    """実行した変更の対象と結果を監査記録へ追加する。"""
    return ctx.audit("create", doc.id)


def check_concurrent_access(ctx: context_types.Context) -> None:
    """組織の更新競合を検出するための書込みフェンスを更新する。"""
    return ctx.fence()
