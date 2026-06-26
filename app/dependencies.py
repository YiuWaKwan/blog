"""FastAPI 依赖。"""

from collections.abc import Generator

from fastapi import Cookie, HTTPException
from sqlalchemy.orm import Session

from app.core.bookmarks_page_auth import (
    BOOKMARKS_PAGE_COOKIE_NAME,
    verify_auth_cookie,
)
from app.core.database_service import db_service
from app.core.unlock_utils import UNLOCK_COOKIE_NAME
from app.services.unlock_service import UnlockService


def get_db() -> Generator[Session]:
    """兼容依赖注入：从连接池借 Session，请求结束归还。"""
    session = db_service.create_session()
    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()


def get_unlocked_post_ids(
    unlock_tokens: str | None = Cookie(default=None, alias=UNLOCK_COOKIE_NAME),
) -> set[str]:
    tokens = UnlockService.parse_tokens(unlock_tokens)
    return UnlockService().get_unlocked_ids("blog_post", tokens)


def get_unlocked_note_ids(
    unlock_tokens: str | None = Cookie(default=None, alias=UNLOCK_COOKIE_NAME),
) -> set[str]:
    tokens = UnlockService.parse_tokens(unlock_tokens)
    return UnlockService().get_unlocked_ids("note", tokens)


def get_unlocked_bookmark_ids(
    unlock_tokens: str | None = Cookie(default=None, alias=UNLOCK_COOKIE_NAME),
) -> set[str]:
    tokens = UnlockService.parse_tokens(unlock_tokens)
    return UnlockService().get_unlocked_ids("bookmark", tokens)


def require_bookmarks_page_access(
    bookmarks_page_auth: str | None = Cookie(
        default=None,
        alias=BOOKMARKS_PAGE_COOKIE_NAME,
    ),
) -> None:
    if not verify_auth_cookie(bookmarks_page_auth):
        raise HTTPException(status_code=403, detail="需要密码访问收藏页")
