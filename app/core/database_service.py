"""
数据库服务 — 应用级单例，维护 PostgreSQL 长连接池。

Python 生态 ORM 说明（对照 Java）：
- SQLAlchemy ORM（本项目使用）≈ JPA / Hibernate：实体类 + Repository 映射表
- SQLAlchemy Core + text() ≈ MyBatis：手写 SQL，适合复杂报表
- 暂无与 MyBatis 完全等价的流行框架；日常开发推荐 SQLAlchemy ORM

连接池：engine 在进程启动时创建，连接从池中取用/归还（长连接），
Session 仍按「一次请求 / 一次事务」短生命周期使用，避免并发脏数据。
"""

from collections.abc import Generator
from contextlib import contextmanager
from typing import Self

from sqlalchemy import create_engine
from sqlalchemy.engine import Engine
from sqlalchemy.orm import Session, sessionmaker

from app.core.config import settings
from app.core.database import Base


class DatabaseService:
    """数据库连接服务（单例）。管理 Engine 连接池与 Session 工厂。"""

    _instance: Self | None = None

    def __new__(cls) -> Self:
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self) -> None:
        if self._initialized:
            return
        self._engine: Engine = create_engine(
            settings.database_url,
            echo=settings.debug,
            pool_pre_ping=True,
            pool_size=10,
            max_overflow=20,
            pool_recycle=3600,
        )
        self._session_factory = sessionmaker(
            autocommit=False,
            autoflush=False,
            bind=self._engine,
        )
        self._initialized = True

    @property
    def engine(self) -> Engine:
        return self._engine

    def create_session(self) -> Session:
        """从连接池获取一个新 Session（调用方负责 close）。"""
        return self._session_factory()

    @contextmanager
    def session_scope(self) -> Generator[Session]:
        """推荐：with db_service.session_scope() as db: ... 自动 commit/rollback/close。"""
        session = self.create_session()
        try:
            yield session
            session.commit()
        except Exception:
            session.rollback()
            raise
        finally:
            session.close()

    @contextmanager
    def read_session(self) -> Generator[Session]:
        """只读 Session：不 commit，仅 close。"""
        session = self.create_session()
        try:
            yield session
        finally:
            session.close()


db_service = DatabaseService()

__all__ = ["DatabaseService", "db_service", "Base"]
