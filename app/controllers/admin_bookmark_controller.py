from typing import Any
from uuid import UUID

from fastapi import APIRouter, HTTPException

from app.core.response import error, success
from app.schemas.requests.admin_bookmark import (
    DeleteBookmarkRequest,
    ImportBookmarksRequest,
    SaveBookmarkCategoryRequest,
    SaveBookmarkRequest,
)
from app.services.bookmark_service import BookmarkService

router = APIRouter(prefix="/api/admin", tags=["admin-bookmark"])


@router.get("/get_bookmarks")
def admin_get_bookmarks(category_id: UUID | None = None) -> dict[str, Any]:
    items = BookmarkService().list_bookmarks_for_admin(category_id)
    return success({"list": [item.model_dump() for item in items]})


@router.get("/get_bookmark")
def admin_get_bookmark(id: UUID) -> dict[str, Any]:
    data = BookmarkService().get_bookmark_for_admin(id)
    if not data:
        raise HTTPException(status_code=404, detail="收藏不存在")
    return success(data.model_dump())


@router.post("/save_bookmark")
def save_bookmark(body: SaveBookmarkRequest) -> dict[str, Any]:
    try:
        bookmark_id = BookmarkService().save_bookmark(body)
    except ValueError as exc:
        return error(400, str(exc))
    return success({"id": str(bookmark_id)})


@router.post("/delete_bookmark")
def delete_bookmark(body: DeleteBookmarkRequest) -> dict[str, Any]:
    try:
        BookmarkService().delete_bookmark(body.id)
    except ValueError as exc:
        return error(404, str(exc))
    return success()


@router.post("/import_bookmarks")
def import_bookmarks(body: ImportBookmarksRequest) -> dict[str, Any]:
    if not body.text.strip():
        return error(400, "导入内容不能为空")
    result = BookmarkService().import_bookmarks_from_text(body.text)
    return success(result)


@router.get("/get_bookmark_categories")
def admin_get_bookmark_categories() -> dict[str, Any]:
    items = BookmarkService().list_categories_for_admin()
    return success({"list": items})


@router.post("/save_bookmark_category")
def save_bookmark_category(body: SaveBookmarkCategoryRequest) -> dict[str, Any]:
    try:
        category_id = BookmarkService().save_bookmark_category(body)
    except ValueError as exc:
        return error(400, str(exc))
    return success({"id": str(category_id)})
