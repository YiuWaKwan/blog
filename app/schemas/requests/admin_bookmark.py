from uuid import UUID

from pydantic import BaseModel, Field


class SaveBookmarkRequest(BaseModel):
    id: UUID | None = None
    title: str | None = None
    url: str
    description: str | None = None
    favicon_url: str | None = None
    is_private: bool = False
    access_password: str | None = None
    category_id: UUID | None = None
    tag_ids: list[UUID] = Field(default_factory=list)
    tag_names: list[str] = Field(default_factory=list)


class DeleteBookmarkRequest(BaseModel):
    id: UUID
