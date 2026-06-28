from typing import Any

from fastapi import APIRouter, Depends

from app.core.response import error, success
from app.dependencies import get_unlocked_bookmark_ids, require_bookmarks_page_access
from app.schemas.requests.bookmark import (
    AddBookmarkRequest,
    DeleteBookmarkRequest,
    VisitBookmarkRequest,
)
from app.services.bookmark_service import BookmarkService

router = APIRouter(prefix="/api", tags=["bookmark"])


@router.get("/get_bookmarks")
def get_bookmarks(
    tag: str | None = None,
    category: str | None = None,
    q: str | None = None,
    unlocked_ids: set[str] = Depends(get_unlocked_bookmark_ids),
    _: None = Depends(require_bookmarks_page_access),
) -> dict[str, Any]:
    items = BookmarkService().list_bookmarks(
        tag_slug=tag,
        category_slug=category,
        query=q,
        unlocked_ids=unlocked_ids,
    )
    return success({"list": [item.model_dump() for item in items]})


@router.get("/get_bookmark_categories")
def get_bookmark_categories(
    _: None = Depends(require_bookmarks_page_access),
) -> dict[str, Any]:
    items = BookmarkService().list_categories()
    return success({"list": items})


@router.post("/add_bookmark")
def add_bookmark(
    body: AddBookmarkRequest,
    _: None = Depends(require_bookmarks_page_access),
) -> dict[str, Any]:
    try:
        bookmark_id = BookmarkService().quick_add_bookmark(
            body.url,
            body.title,
            body.category_id,
        )
    except ValueError as exc:
        return error(400, str(exc))
    return success({"id": str(bookmark_id)})


@router.post("/visit_bookmark")
def visit_bookmark(
    body: VisitBookmarkRequest,
    unlocked_ids: set[str] = Depends(get_unlocked_bookmark_ids),
    _: None = Depends(require_bookmarks_page_access),
) -> dict[str, Any]:
    try:
        BookmarkService().record_visit(body.id, unlocked_ids)
    except ValueError as exc:
        return error(400, str(exc))
    return success()


@router.post("/delete_bookmark")
def delete_bookmark(
    body: DeleteBookmarkRequest,
    _: None = Depends(require_bookmarks_page_access),
) -> dict[str, Any]:
    try:
        BookmarkService().soft_delete_bookmark(body.id)
    except ValueError as exc:
        return error(404, str(exc))
    return success()
