from pydantic import Field

from app.schemas.page import PageQuery


class AdminPostListQuery(PageQuery):
    """后台博客列表 — 继承 PageQuery。"""

    limit: int = Field(default=20, ge=1, le=100)
    keyword: str | None = Field(default=None, description="标题关键词")


class AdminNoteListQuery(PageQuery):
    """后台笔记列表 — 继承 PageQuery。"""

    limit: int = Field(default=20, ge=1, le=100)
    keyword: str | None = Field(default=None, description="标题关键词")
