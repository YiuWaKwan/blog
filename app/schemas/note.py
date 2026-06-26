from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

from app.schemas.common import TagBrief


class NoteListItem(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    title: str
    slug: str
    excerpt: str | None = None
    cover_image_url: str | None = None
    published_at: datetime | None = None
    reading_time_minutes: int | None = 0
    is_private: bool = False
    category_slug: str | None = None
    category_name: str | None = None
    tags: list[TagBrief] = Field(default_factory=list)


class NoteDetail(NoteListItem):
    content: str = ""
    view_count: int = 0


class NoteDetailResult(BaseModel):
    requires_unlock: bool = False
    note_id: UUID | None = None
    detail: NoteDetail | None = None
