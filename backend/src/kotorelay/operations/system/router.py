"""公開可能な死活確認のみを提供する。"""

from fastapi import APIRouter

router = APIRouter(prefix="/api", tags=["システム"])


@router.get("/health", summary="死活確認", operation_id="health")
def health() -> dict[str, str]:
    return {"status": "ok", "product": "KotoRelay"}
