from typing import Any

from fastapi import APIRouter, Depends, HTTPException

from app.core.response import error, success
from app.dependencies import get_unlocked_post_ids
from app.schemas.queries.post import PostListQuery
from app.services.post_service import PostService

router = APIRouter(prefix="/api", tags=["post"])


@router.post("/get_posts")
def get_posts(body: PostListQuery) -> dict[str, Any]:
    """
    博客列表 — 完整参考示例。

    page/limit/tag 共 3 个参数，按项目约定使用 POST + JSON body。
    Service 内部通过 DatabaseService 长连接池获取 Session。
    """
    data = PostService().list_posts(body)
    return success(data.model_dump())


@router.get("/get_post")
def get_post(
    slug: str,
    unlocked_ids: set[str] = Depends(get_unlocked_post_ids),
) -> dict[str, Any]:
    """博客详情 — 完整参考示例。"""
    result = PostService().get_post_by_slug(slug, unlocked_ids=unlocked_ids)
    if result.requires_unlock:
        return error(
            403,
            "需要密码解锁",
            data={"requires_unlock": True, "id": str(result.post_id)},
        )
    if not result.detail:
        raise HTTPException(status_code=404, detail="文章不存在")
    return success(result.detail.model_dump())


@router.get("/get_site_stats")
def get_site_stats() -> dict[str, Any]:
    data = PostService().get_dashboard_stats()
    return success(data.model_dump())
