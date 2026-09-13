"""submit_versionのHTTP入力と業務処理の順序を宣言する。"""

from uuid import UUID

from fastapi import APIRouter

from kotorelay.generated import models
from kotorelay.http_types import Key
from kotorelay.operations.documents.submit_version import functions as f
from kotorelay.operations.documents.submit_version.contract import CONTRACT
from kotorelay.operations.documents.submit_version.response_builders import build_response
from kotorelay.operations.documents.submit_version.samples import SAMPLES
from kotorelay.operations.documents.submit_version.schemas import Submit
from kotorelay.runtime import Ctx

router = APIRouter(prefix="/api/documents", tags=["文書"])


@router.post(
    "/{document_id}/submissions",
    status_code=201,
    summary="版を確定して承認申請",
    operation_id="submit_version",
    openapi_extra=CONTRACT.openapi_extra(SAMPLES),
)
def submit_version(ctx: Ctx, document_id: UUID, data: Submit, key: Key) -> models.VersionsRow:
    return build_response(f.submit(ctx, str(document_id), data, str(key)))
