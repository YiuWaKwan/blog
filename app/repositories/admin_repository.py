from sqlalchemy import select

from app.models.admin_user import AdminUser
from app.repositories.base_repository import BaseRepository


class AdminRepository(BaseRepository):
    def get_by_username(self, username: str) -> AdminUser | None:
        return self.db.scalars(
            select(AdminUser).where(AdminUser.username == username)
        ).first()
