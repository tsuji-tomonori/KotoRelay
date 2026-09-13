"""groupsのAPIごとのルーターを登録する。"""

from fastapi import APIRouter

from kotorelay.operations.groups.change_membership.router import router as change_membership
from kotorelay.operations.groups.get_identity.router import router as get_identity
from kotorelay.operations.groups.list_members.router import router as list_members

router = APIRouter()
router.include_router(get_identity)
router.include_router(list_members)
router.include_router(change_membership)
