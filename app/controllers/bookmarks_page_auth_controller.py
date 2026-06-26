from typing import Any

from fastapi import APIRouter, Response

from app.core.bookmarks_page_auth import (
    BOOKMARKS_PAGE_COOKIE_NAME,
    BOOKMARKS_PAGE_MAX_AGE,
    create_auth_cookie,
    verify_page_password,
)
from app.core.config import settings
from app.core.response import error, success
from app.schemas.requests.bookmarks_page_unlock import BookmarksPageUnlockRequest

router = APIRouter(prefix="/api", tags=["auth"])


@router.post("/unlock_bookmarks_page")
def unlock_bookmarks_page(
    body: BookmarksPageUnlockRequest,
    response: Response,
) -> dict[str, Any]:
    if not settings.bookmarks_page_password:
        return error(503, "未配置收藏页访问密码")

    if not verify_page_password(body.password):
        return error(403, "密码错误")

    token = create_auth_cookie()
    if not token:
        return error(503, "未配置收藏页访问密码")

    response.set_cookie(
        key=BOOKMARKS_PAGE_COOKIE_NAME,
        value=token,
        httponly=True,
        samesite="lax",
        max_age=BOOKMARKS_PAGE_MAX_AGE,
    )
    return success({"unlocked": True})
