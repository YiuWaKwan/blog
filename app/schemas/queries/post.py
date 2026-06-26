from pydantic import Field

from app.schemas.page import PageQuery


class PostListQuery(PageQuery):
    """博客列表查询 — 继承 PageQuery。"""

    tag: str | None = Field(default=None, description="按标签 slug 筛选")
