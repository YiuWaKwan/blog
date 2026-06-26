"""ORM 基类 — Engine 与连接池由 DatabaseService 统一管理。"""

from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    pass
