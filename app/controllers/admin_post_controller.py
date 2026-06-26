from typing import Any
from uuid import UUID

from fastapi import APIRouter, HTTPException

from app.core.response import error, success
from app.schemas.queries.admin import AdminPostListQuery
from app.schemas.requests.admin_login import AdminLoginRequest
from app.schemas.requests.admin_post import DeletePostRequest, SavePostRequest
from app.services.auth_service import AuthService
from app.services.post_service import PostService

router = APIRouter(prefix="/api/admin", tags=["admin-post"])


@router.post("/login")
def admin_login(body: AdminLoginRequest) -> dict[str, Any]:
    if not AuthService().login(body.username, body.password):
        return error(401, "用户名或密码错误")
    return success({"token": "ok"})


@router.post("/logout")
def admin_logout() -> dict[str, Any]:
    return success()


@router.get("/get_dashboard")
def get_dashboard() -> dict[str, Any]:
    data = PostService().get_dashboard_stats()
    return success(data.model_dump())


@router.post("/get_posts")
def admin_get_posts(body: AdminPostListQuery) -> dict[str, Any]:
    data = PostService().list_posts_for_admin(body)
    return success(data.model_dump())


@router.get("/get_post")
def admin_get_post(id: UUID) -> dict[str, Any]:
    data = PostService().get_post_for_admin(id)
    if not data:
        raise HTTPException(status_code=404, detail="文章不存在")
    return success(data.model_dump())


@router.post("/save_post")
def save_post(body: SavePostRequest) -> dict[str, Any]:
    try:
        post_id = PostService().save_post(body)
    except ValueError as exc:
        return error(400, str(exc))
    return success({"id": str(post_id)})


@router.post("/delete_post")
def delete_post(body: DeletePostRequest) -> dict[str, Any]:
    try:
        PostService().delete_post(body.id)
    except ValueError as exc:
        return error(404, str(exc))
    return success()
