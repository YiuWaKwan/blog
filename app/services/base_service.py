"""Service 基类 — 通过 DatabaseService 获取数据库 Session。"""

from collections.abc import Generator
from contextlib import contextmanager

from sqlalchemy.orm import Session

from app.core.database_service import db_service


class BaseService:
    """
    业务 Service 基类。

    子类在方法内使用:
        with self.read_session() as db:
            ...
    或写操作:
        with self.session_scope() as db:
            ...
    """

    def __init__(self) -> None:
        self.db = db_service

    @contextmanager
    def session_scope(self) -> Generator[Session]:
        with self.db.session_scope() as session:
            yield session

    @contextmanager
    def read_session(self) -> Generator[Session]:
        with self.db.read_session() as session:
            yield session
