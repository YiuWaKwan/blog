from app.core.security import verify_password
from app.repositories.admin_repository import AdminRepository
from app.services.base_service import BaseService


class AuthService(BaseService):
    def login(self, username: str, password: str) -> bool:
        with self.read_session() as db:
            user = AdminRepository(db).get_by_username(username)

        if not user:
            return False
        return verify_password(password, user.password_hash)
