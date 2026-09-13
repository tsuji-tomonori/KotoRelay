"""submit_versionのHTTP入力と業務処理の順序を宣言する。"""

from __future__ import annotations

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
from kotorelay.schemas import ManifestImage

router = APIRouter(prefix="/api/documents", tags=["文書"])


@router.post(
    "/{document_id}/submissions",
    status_code=201,
    summary="版を確定して承認申請",
    operation_id="submit_version",
    openapi_extra=CONTRACT.openapi_extra(SAMPLES),
)
def submit_version(ctx: Ctx, document_id: UUID, data: Submit, key: Key) -> models.VersionsRow:
    doc = f.document_doc(ctx, document_id)
    request = str(document_id) + data.model_dump_json()
    cached = f.find_previous_result(request, ctx, key)
    if cached:
        return build_response(f.build_submit_version(cached))
    row = next(d for d in f.drafts_list(ctx) if d.document_id == doc.id)
    f.validate_draft_revision(row, data)
    images: list[ManifestImage] = []
    for placement in f.read_placements(row):
        asset = f.assets_get(ctx, placement)[0]
        ocr = f.ocr_runs_get(ctx, placement)[0]
        f.require_confirmed_ocr(ocr)
        f.verify_image(asset, ctx)
        f.verify_ocr(ocr, ctx)
        images.append(f.build_manifest_image(placement, asset.sha256, ocr.result_hash))
    f.verify_body(row, ctx)
    manifest = f.serialize_manifest(row.body_hash, images)
    version = f.build_version(manifest, ctx, doc, row)
    f.versions_insert(ctx, version)
    f.submissions_insert(ctx, doc, version)
    f.documents_update(ctx, doc)
    f.record_submit_version_audit(ctx, doc, version)
    f.remember_submit_version_result(request, ctx, key, version)
    f.check_concurrent_access(ctx)
    return build_response(version)
