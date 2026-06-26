from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict


class ApiResponse[T](BaseModel):
    code: int = 0
    message: str = "ok"
    data: T | None = None


class PageData[T](BaseModel):
    list: list[T]
    total: int
    page: int
    limit: int


class TagBrief(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    name: str
    slug: str


class TagWithStats(TagBrief):
    blog_count: int = 0
    note_count: int = 0
    bookmark_count: int = 0
    total_count: int = 0
