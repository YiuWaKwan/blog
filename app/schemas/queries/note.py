from pydantic import Field

from app.schemas.page import PageQuery


class NoteListQuery(PageQuery):
    """笔记列表查询 — 继承 PageQuery。"""

    tag: str | None = Field(default=None, description="按标签 slug 筛选")
    category: str | None = Field(default=None, description="按分类 slug 筛选")
