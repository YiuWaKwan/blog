from typing import Any
from uuid import UUID

from fastapi import APIRouter, HTTPException

from app.core.response import error, success
from app.schemas.requests.admin_tag import DeleteTagRequest, SaveTagRequest
from app.services.tag_service import TagService

router = APIRouter(prefix="/api/admin", tags=["admin-tag"])


@router.get("/get_tags")
def admin_get_tags(q: str | None = None, sort: str | None = None) -> dict[str, Any]:
    items = TagService().list_for_admin(q, sort)
    return success({"list": [item.model_dump() for item in items]})


@router.get("/get_tag")
def admin_get_tag(id: UUID) -> dict[str, Any]:
    data = TagService().get_tag_for_admin(id)
    if not data:
        raise HTTPException(status_code=404, detail="标签不存在")
    return success(data.model_dump())


@router.post("/save_tag")
def save_tag(body: SaveTagRequest) -> dict[str, Any]:
    try:
        tag_id = TagService().save_tag(body)
    except ValueError as exc:
        return error(400, str(exc))
    return success({"id": str(tag_id)})


@router.post("/delete_tag")
def delete_tag(body: DeleteTagRequest) -> dict[str, Any]:
    try:
        TagService().delete_tag(body.id)
    except ValueError as exc:
        return error(404, str(exc))
    return success()
