from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

from app.schemas.common import TagBrief


class BookmarkListItem(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    title: str
    url: str = ""
    description: str | None = None
    favicon_url: str | None = None
    is_private: bool = False
    requires_unlock: bool = False
    category_slug: str | None = None
    category_name: str | None = None
    tags: list[TagBrief] = Field(default_factory=list)


class BookmarkDetailResult(BaseModel):
    requires_unlock: bool = False
    bookmark_id: UUID | None = None
    detail: BookmarkListItem | None = None


class BookmarkCategoryBrief(BaseModel):
    id: UUID
    name: str
    slug: str
    sort_order: int = 0
