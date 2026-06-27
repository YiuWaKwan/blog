from uuid import UUID

from pydantic import BaseModel


class AddBookmarkRequest(BaseModel):
    url: str
    title: str | None = None


class VisitBookmarkRequest(BaseModel):
    id: UUID
