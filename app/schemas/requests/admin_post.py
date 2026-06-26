from uuid import UUID

from pydantic import BaseModel, Field


class SavePostRequest(BaseModel):
    id: UUID | None = None
    title: str
    slug: str
    excerpt: str | None = None
    content: str = ""
    cover_image_url: str | None = None
    is_published: bool = False
    is_private: bool = False
    access_password: str | None = None
    tag_ids: list[UUID] = Field(default_factory=list)
    tag_names: list[str] = Field(default_factory=list)


class DeletePostRequest(BaseModel):
    id: UUID
