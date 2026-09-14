"""reviewsのdecide_reviewの業務判定と処理を実行する。"""

from __future__ import annotations

import uuid

import kotorelay.context as context_types
import kotorelay.generated.models as models
import kotorelay.operations.reviews.decide_review.generated.queries as q
import kotorelay.operations.reviews.decide_review.schemas as request_schemas
from kotorelay.context import new_id, now
from kotorelay.errors import require


def submissions_get(
    ctx: context_types.Context, submission_id: uuid.UUID
) -> list[q.SubmissionsGetRow]:
    """現在の組織に属する指定の承認申請について、対象の文書版・審査状態・判断者・理由を取得する。"""
    return q.submissions_get(
        ctx.db, q.SubmissionsGetParams(organization_id=ctx.org, id=str(submission_id))
    )


def require_submission(rows: list[q.SubmissionsGetRow]) -> None:
    """対象の承認申請が存在することを確認する。"""
    return require(bool(rows))


def document_doc(
    ctx: context_types.Context, submission: q.SubmissionsGetRow
) -> models.DocumentsRow:
    """文書を取得して要求された操作の権限を確認する。"""
    return ctx.document(submission.document_id, "review")


def find_previous_result(request: str, ctx: context_types.Context, key: uuid.UUID) -> str | None:
    """要求内容の一致を確認して同じ冪等キーの記録済み結果を取得する。"""
    return ctx.idempotent_result(str(key), "decide", request)


def build_decide_review(cached: str) -> models.SubmissionsRow:
    """後続処理に渡すデータを組み立てる。"""
    return models.SubmissionsRow.model_validate_json(cached)


def require_pending_submission(submission: q.SubmissionsGetRow) -> None:
    """未決裁の申請であることを確認する。"""
    return require(submission.status == "pending", "conflict", 409)


def version_version(
    doc: models.DocumentsRow, ctx: context_types.Context, submission: q.SubmissionsGetRow
) -> models.VersionsRow:
    """対象文書に属する確定版を取得する。"""
    return ctx.version(doc, submission.version_id)


def prevent_self_approval(version: models.VersionsRow, ctx: context_types.Context) -> None:
    """版の作成者による自己承認を拒否する。"""
    return require(version.created_by != ctx.user.id, "self_approval", 403)


def validate_manifest_hash(
    submission: q.SubmissionsGetRow, data: request_schemas.Decide, version: models.VersionsRow
) -> None:
    """申請・確認画面・確定版のmanifestハッシュが一致することを確認する。"""
    return require(
        submission.manifest_hash == data.manifest_hash == version.manifest_hash, "conflict", 409
    )


def require_rejection_reason(data: request_schemas.Decide) -> None:
    """却下するときに理由が入力されていることを確認する。"""
    return require(data.decision != "rejected" or bool(data.reason.strip()), "reason_required", 422)


def build_updated(
    submission: q.SubmissionsGetRow, data: request_schemas.Decide, ctx: context_types.Context
) -> q.SubmissionsGetRow:
    """後続処理に渡すデータを組み立てる。"""
    return submission.model_copy(
        update={
            "status": data.decision,
            "reason": data.reason,
            "decided_by": ctx.user.id,
            "decided_at": now(),
        }
    )


def submissions_update(ctx: context_types.Context, updated: q.SubmissionsGetRow) -> int:
    """現在の組織に属する指定の承認申請について、対象の文書版・審査状態・判断者・理由を更新する。"""
    return q.submissions_update(
        ctx.db, q.SubmissionsUpdateParams.model_validate(updated, from_attributes=True)
    )


def is_approved(data: request_schemas.Decide) -> bool:
    """申請を承認する決裁かを判定する。"""
    return bool(data.decision == "approved")


def versions_get(ctx: context_types.Context, version_id: str) -> list[q.VersionsGetRow]:
    """現在の組織に属する指定の文書版について、確定した本文の保存先と画像構成・検証用ハッシュを取得する。"""
    return q.versions_get(ctx.db, q.VersionsGetParams(organization_id=ctx.org, id=version_id))


def is_newer_publication(previous: list[q.VersionsGetRow], version: models.VersionsRow) -> bool:
    """今回の版が公開中の版より新しいかを判定する。"""
    return bool(not previous or previous[0].number < version.number)


def documents_update(
    ctx: context_types.Context, doc: models.DocumentsRow, version: models.VersionsRow
) -> int:
    """現在の組織に属する指定の文書について、文書の所有部署・公開範囲・状態・公開版の参照を更新する。"""
    return q.documents_update(
        ctx.db,
        q.DocumentsUpdateParams.model_validate(
            doc.model_copy(
                update={
                    "latest_version_id": version.id,
                    "revision": doc.revision + 1,
                    "updated_at": now(),
                }
            ),
            from_attributes=True,
        ),
    )


def outbox_insert(
    ctx: context_types.Context, doc: models.DocumentsRow, version: models.VersionsRow
) -> int:
    """現在の組織の反映・削除ジョブを、対象文書と版・処理種別を指定して登録する。"""
    return q.outbox_insert(
        ctx.db,
        q.OutboxInsertParams(
            id=new_id(),
            organization_id=ctx.org,
            document_id=doc.id,
            version_id=version.id,
            kind="index",
            status="pending",
            attempts=0,
            error_code="",
            created_at=now(),
        ),
    )


def record_decide_review_audit(
    ctx: context_types.Context,
    doc: models.DocumentsRow,
    version: models.VersionsRow,
    submission: q.SubmissionsGetRow,
    updated: q.SubmissionsGetRow,
    data: request_schemas.Decide,
) -> None:
    """実行した変更の対象と結果を監査記録へ追加する。"""
    return ctx.audit("review", doc.id, version.id, submission.status, updated.status, data.reason)


def remember_decide_review_result(
    request: str, ctx: context_types.Context, key: uuid.UUID, updated: q.SubmissionsGetRow
) -> None:
    """同じ要求を安全に再試行できるよう冪等キーと結果を記録する。"""
    return ctx.remember(str(key), "decide", request, updated.model_dump_json())


def check_concurrent_access(ctx: context_types.Context) -> None:
    """組織の更新競合を検出するための書込みフェンスを更新する。"""
    return ctx.fence()


def has_previous_result(cached: str | None) -> bool:
    """同じ操作IDの処理結果が保存されている。"""
    return bool(cached)


def has_published_version(doc: models.DocumentsRow) -> bool:
    """文書に公開済みの版がある。"""
    return bool(doc.latest_version_id)
