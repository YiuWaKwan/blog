from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

from app.schemas.common import TagBrief, TagWithStats


class DashboardData(BaseModel):
    posts: int = 0
    notes: int = 0
    bookmarks: int = 0
    tags: int = 0
    top_tags: list[TagWithStats] = Field(default_factory=list)


class AdminPostListItem(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    title: str
    slug: str
    is_published: bool = False
    is_private: bool = False
    published_at: datetime | None = None
    updated_at: datetime | None = None
    tags: list[TagBrief] = Field(default_factory=list)


class AdminPostDetail(BaseModel):
    id: UUID
    title: str
    slug: str
    excerpt: str | None = None
    content: str = ""
    cover_image_url: str | None = None
    is_published: bool = False
    is_private: bool = False
    tag_ids: list[UUID] = Field(default_factory=list)
    tags: list[TagBrief] = Field(default_factory=list)


class AdminNoteListItem(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    title: str
    slug: str
    is_published: bool = False
    is_private: bool = False
    published_at: datetime | None = None
    updated_at: datetime | None = None
    category_name: str | None = None
    tags: list[TagBrief] = Field(default_factory=list)


class AdminNoteDetail(BaseModel):
    id: UUID
    title: str
    slug: str
    excerpt: str | None = None
    content: str = ""
    cover_image_url: str | None = None
    is_published: bool = False
    is_private: bool = False
    category_id: UUID | None = None
    tag_ids: list[UUID] = Field(default_factory=list)
    tags: list[TagBrief] = Field(default_factory=list)


class AdminBookmarkListItem(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    title: str
    url: str
    description: str | None = None
    is_private: bool = False
    category_name: str | None = None
    tags: list[TagBrief] = Field(default_factory=list)


class AdminBookmarkDetail(BaseModel):
    id: UUID
    title: str
    url: str
    description: str | None = None
    favicon_url: str | None = None
    is_private: bool = False
    category_id: UUID | None = None
    tag_ids: list[UUID] = Field(default_factory=list)
    tags: list[TagBrief] = Field(default_factory=list)


class AdminTagListItem(TagWithStats):
    created_at: datetime | None = None
