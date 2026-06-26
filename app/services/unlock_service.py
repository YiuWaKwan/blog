from uuid import UUID

from app.core.security import verify_password
from app.core.unlock_utils import UNLOCK_COOKIE_NAME, append_unlock_token, parse_unlock_tokens
from app.repositories.bookmark_repository import BookmarkRepository
from app.repositories.note_repository import NoteRepository
from app.repositories.post_repository import PostRepository
from app.repositories.unlock_repository import UnlockRepository
from app.services.base_service import BaseService


RESOURCE_MODELS = {
    "blog_post": (PostRepository, "get_by_id"),
    "note": (NoteRepository, "get_by_id"),
    "bookmark": (BookmarkRepository, "get_by_id"),
}


class UnlockService(BaseService):
    def get_unlocked_ids(
        self,
        resource_type: str,
        tokens: list[str],
    ) -> set[str]:
        if not tokens:
            return set()

        with self.read_session() as db:
            unlocks = UnlockRepository(db).get_valid_unlocks(tokens)

        return {
            str(item.resource_id)
            for item in unlocks
            if item.resource_type == resource_type
        }

    def unlock_content(
        self,
        resource_type: str,
        resource_id: UUID,
        password: str,
        cookie_value: str | None,
    ) -> tuple[bool, str | None, str]:
        if resource_type not in RESOURCE_MODELS:
            return False, None, "不支持的资源类型"

        repo_cls, getter = RESOURCE_MODELS[resource_type]

        with self.session_scope() as db:
            repo = repo_cls(db)
            resource = getattr(repo, getter)(resource_id)

            if not resource:
                return False, None, "资源不存在"

            if not resource.is_private:
                return True, cookie_value, "ok"

            if not resource.access_password_hash:
                return False, None, "该内容未配置访问密码"

            if not verify_password(password, resource.access_password_hash):
                return False, None, "密码错误"

            unlock = UnlockRepository(db).create_unlock(resource_type, resource_id)
            new_cookie = append_unlock_token(cookie_value, unlock.session_token)
            return True, new_cookie, "ok"

    @staticmethod
    def cookie_name() -> str:
        return UNLOCK_COOKIE_NAME

    @staticmethod
    def parse_tokens(cookie_value: str | None) -> list[str]:
        return parse_unlock_tokens(cookie_value)
