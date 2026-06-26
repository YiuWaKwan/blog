from pydantic import Field

from pydantic import BaseModel


class SearchQuery(BaseModel):
    q: str = Field(min_length=1, max_length=100)
    limit: int = Field(default=20, ge=1, le=50)
