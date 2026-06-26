"""分页查询基类 — 所有带分页的 GET 查询 DTO 继承此类。"""

from pydantic import BaseModel, Field


class PageQuery(BaseModel):
    """分页参数父类：统一接收 page、limit，并提供 offset 计算。"""

    page: int = Field(default=1, ge=1, description="页码，从 1 开始")
    limit: int = Field(default=10, ge=1, le=100, description="每页条数")

    @property
    def offset(self) -> int:
        return (self.page - 1) * self.limit
