"""documentsのAPIごとのルーターを登録する。"""

from fastapi import APIRouter

from kotorelay.operations.documents.change_policy.router import router as change_policy
from kotorelay.operations.documents.create_document.router import router as create_document
from kotorelay.operations.documents.get_draft.router import router as get_draft
from kotorelay.operations.documents.list_documents.router import router as list_documents
from kotorelay.operations.documents.read_document.router import router as read_document
from kotorelay.operations.documents.save_draft.router import router as save_draft
from kotorelay.operations.documents.submit_version.router import router as submit_version
from kotorelay.operations.documents.version_diff.router import router as version_diff
from kotorelay.operations.documents.version_history.router import router as version_history

router = APIRouter()
router.include_router(create_document)
router.include_router(list_documents)
router.include_router(get_draft)
router.include_router(save_draft)
router.include_router(submit_version)
router.include_router(read_document)
router.include_router(version_history)
router.include_router(version_diff)
router.include_router(change_policy)
