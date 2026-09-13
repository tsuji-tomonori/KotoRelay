"""change_policyのHTTP入力と業務処理の順序を宣言する。"""

from uuid import UUID

from fastapi import APIRouter

from kotorelay.generated import models
from kotorelay.operations.documents.change_policy import functions as f
from kotorelay.operations.documents.change_policy.contract import CONTRACT
from kotorelay.operations.documents.change_policy.response_builders import build_response
from kotorelay.operations.documents.change_policy.samples import SAMPLES
from kotorelay.operations.documents.change_policy.schemas import ChangePolicy
from kotorelay.runtime import Ctx

router = APIRouter(prefix="/api/documents", tags=["文書"])


@router.put(
    "/{document_id}/policy",
    summary="リーダーが公開範囲・公開停止・削除を管理",
    operation_id="change_policy",
    openapi_extra=CONTRACT.openapi_extra(SAMPLES),
)
def change_policy(ctx: Ctx, document_id: UUID, data: ChangePolicy) -> models.DocumentsRow:
    return build_response(f.policy(ctx, str(document_id), data))
