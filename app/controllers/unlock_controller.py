from typing import Any

from fastapi import APIRouter, Cookie, Response

from app.core.response import error, success
from app.core.unlock_utils import UNLOCK_COOKIE_NAME
from app.schemas.requests.unlock import UnlockRequest
from app.services.unlock_service import UnlockService

router = APIRouter(prefix="/api", tags=["auth"])


@router.post("/unlock")
def unlock(
    body: UnlockRequest,
    response: Response,
    unlock_tokens: str | None = Cookie(default=None, alias=UNLOCK_COOKIE_NAME),
) -> dict[str, Any]:
    from uuid import UUID

    try:
        resource_id = UUID(body.id)
    except ValueError:
        return error(400, "无效的资源 ID")

    ok, new_cookie, message = UnlockService().unlock_content(
        body.type,
        resource_id,
        body.password,
        unlock_tokens,
    )
    if not ok:
        return error(403, message)

    if new_cookie:
        response.set_cookie(
            key=UNLOCK_COOKIE_NAME,
            value=new_cookie,
            httponly=True,
            samesite="lax",
            max_age=86400,
        )

    return success({"unlocked": True})
