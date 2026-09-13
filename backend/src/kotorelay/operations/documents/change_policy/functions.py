"""documentsのchange_policyの業務判定と処理を実行する。"""

from __future__ import annotations

import json
import uuid

import kotorelay.context as context_types
import kotorelay.generated.models as models
import kotorelay.operations.documents.change_policy.schemas as request_schemas
from kotorelay.context import new_id, now
from kotorelay.errors import require
from kotorelay.operations.documents.change_policy.generated import queries as q


def document_doc(ctx: context_types.Context, document_id: uuid.UUID) -> models.DocumentsRow:
    """文書を取得して要求された操作の権限を確認する。"""
    return ctx.document(str(document_id), "manage")


def validate_document_revision(
    doc: models.DocumentsRow, data: request_schemas.ChangePolicy
) -> None:
    """文書が読み込み時点から変更されていないことを確認する。"""
    return require(doc.revision == data.revision, "conflict", 409)


def require_deletion_reason(data: request_schemas.ChangePolicy) -> None:
    """文書を削除するときに理由が入力されていることを確認する。"""
    return require(data.status != "deleted" or bool(data.reason.strip()), "reason_required", 422)


def collect_departments(ctx: context_types.Context) -> set[str]:
    """処理対象の識別子を重複なく取り出す。"""
    return {
        d.id
        for d in q.departments_list(ctx.db, q.DepartmentsListParams(organization_id=ctx.org))
        if d.active
    }


def validate_shared_departments(departments: set[str], data: request_schemas.ChangePolicy) -> None:
    """共有先の全部署が現在の組織に存在することを確認する。"""
    return require(set(data.shared_departments) <= departments, "forbidden", 422)


def build_updated(
    doc: models.DocumentsRow, data: request_schemas.ChangePolicy
) -> models.DocumentsRow:
    """後続処理に渡すデータを組み立てる。"""
    return doc.model_copy(
        update={
            "visibility": data.visibility,
            "shared_departments": json.dumps(data.shared_departments),
            "status": data.status,
            "revision": doc.revision + 1,
            "updated_at": now(),
        }
    )


def documents_update(ctx: context_types.Context, updated: models.DocumentsRow) -> int:
    """現在の組織に属する指定の文書について、文書の所有部署・公開範囲・状態・公開版の参照を更新する。"""
    return q.documents_update(
        ctx.db, q.DocumentsUpdateParams.model_validate(updated, from_attributes=True)
    )


def outbox_insert(
    ctx: context_types.Context, doc: models.DocumentsRow, data: request_schemas.ChangePolicy
) -> int:
    """現在の組織の反映・削除ジョブを、対象文書と版・処理種別を指定して登録する。"""
    return q.outbox_insert(
        ctx.db,
        q.OutboxInsertParams(
            id=new_id(),
            organization_id=ctx.org,
            document_id=doc.id,
            version_id=doc.latest_version_id,
            kind="purge" if data.status == "deleted" else "index",
            status="pending",
            attempts=0,
            error_code="",
            created_at=now(),
        ),
    )


def record_change_policy_audit(
    ctx: context_types.Context, doc: models.DocumentsRow, data: request_schemas.ChangePolicy
) -> None:
    """実行した変更の対象と結果を監査記録へ追加する。"""
    return ctx.audit("policy", doc.id, before=doc.status, after=data.status, reason=data.reason)


def check_concurrent_access(ctx: context_types.Context) -> None:
    """組織の更新競合を検出するための書込みフェンスを更新する。"""
    return ctx.fence()
