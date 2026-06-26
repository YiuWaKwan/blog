from pydantic import BaseModel, Field


class PopularTagsQuery(BaseModel):
    """热门标签 — 非分页，仅 limit。"""

    limit: int = Field(default=8, ge=1, le=50)
