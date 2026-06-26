"""Repository 基类 — 持有当前事务的 Session。"""

from sqlalchemy.orm import Session


class BaseRepository:
    def __init__(self, db: Session):
        self.db = db
