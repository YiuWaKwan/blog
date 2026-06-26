from uuid import UUID

from pydantic import BaseModel


class SaveTagRequest(BaseModel):
    id: UUID | None = None
    name: str
    slug: str | None = None


class DeleteTagRequest(BaseModel):
    id: UUID
