from uuid import UUID

from pydantic import BaseModel


class AddBookmarkRequest(BaseModel):
    url: str
    title: str | None = None
    category_id: UUID | None = None


class VisitBookmarkRequest(BaseModel):
    id: UUID


class DeleteBookmarkRequest(BaseModel):
    id: UUID
