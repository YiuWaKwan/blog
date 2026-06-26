from datetime import datetime

from pydantic import BaseModel


class SearchResultItem(BaseModel):
    content_type: str
    title: str
    slug: str
    excerpt: str | None = None
    published_at: datetime | None = None
