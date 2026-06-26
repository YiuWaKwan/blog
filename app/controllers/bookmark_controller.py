from typing import Any

from fastapi import APIRouter, Cookie, Depends

from app.core.response import success
from app.dependencies import get_unlocked_bookmark_ids, require_bookmarks_page_access
from app.services.bookmark_service import BookmarkService

router = APIRouter(prefix="/api", tags=["bookmark"])


@router.get("/get_bookmarks")
def get_bookmarks(
    tag: str | None = None,
    category: str | None = None,
    unlocked_ids: set[str] = Depends(get_unlocked_bookmark_ids),
    _: None = Depends(require_bookmarks_page_access),
) -> dict[str, Any]:
    items = BookmarkService().list_bookmarks(
        tag_slug=tag,
        category_slug=category,
        unlocked_ids=unlocked_ids,
    )
    return success({"list": [item.model_dump() for item in items]})
