from typing import Any

from fastapi import APIRouter, Depends, HTTPException

from app.core.response import success
from app.dependencies import get_unlocked_bookmark_ids
from app.schemas.queries.tag import PopularTagsQuery
from app.services.tag_service import TagService

router = APIRouter(prefix="/api", tags=["tag"])


@router.get("/get_tags")
def get_tags() -> dict[str, Any]:
    items = TagService().list_tags()
    return success({"list": [item.model_dump() for item in items]})


@router.get("/get_tag")
def get_tag(
    slug: str,
    content_type: str = "all",
    unlocked_bookmark_ids: set[str] = Depends(get_unlocked_bookmark_ids),
) -> dict[str, Any]:
    data = TagService().get_tag_detail(slug, content_type, unlocked_bookmark_ids)
    if not data:
        raise HTTPException(status_code=404, detail="标签不存在")
    return success(data)


@router.get("/get_popular_tags")
def get_popular_tags(query: PopularTagsQuery = Depends()) -> dict[str, Any]:
    items = TagService().list_popular(query.limit)
    return success({"list": [item.model_dump() for item in items]})
