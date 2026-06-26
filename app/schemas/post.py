from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

from app.schemas.common import TagBrief


class PostListItem(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    title: str
    slug: str
    excerpt: str | None = None
    cover_image_url: str | None = None
    published_at: datetime | None = None
    reading_time_minutes: int | None = 0
    is_private: bool = False
    tags: list[TagBrief] = Field(default_factory=list)


class PostDetail(PostListItem):
    content: str = ""
    view_count: int = 0


class PostDetailResult(BaseModel):
    """Service 层返回给 Controller 的包装类型。"""

    requires_unlock: bool = False
    post_id: UUID | None = None
    detail: PostDetail | None = None
