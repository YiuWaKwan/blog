from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

from app.schemas.common import TagBrief, TagWithStats


class TagDetail(BaseModel):
    tag: TagWithStats
    items: list[dict] = Field(default_factory=list)


class TagContentItem(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    title: str
    slug: str | None = None
    url: str | None = None
    content_type: str
    published_at: datetime | None = None
    tags: list[TagBrief] = Field(default_factory=list)
