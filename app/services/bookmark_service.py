from uuid import UUID

from app.core.datetime_utils import utc_now
from app.models.bookmark import Bookmark
from app.repositories.bookmark_repository import BookmarkRepository
from app.repositories.tag_repository import TagRepository
from app.schemas.admin import AdminBookmarkDetail, AdminBookmarkListItem
from app.schemas.bookmark import BookmarkDetailResult, BookmarkListItem
from app.schemas.common import TagBrief
from app.schemas.requests.admin_bookmark import SaveBookmarkRequest
from app.services.base_service import BaseService
from app.services.content_helpers import apply_private_password


def resolve_bookmark_title(title: str | None, url: str) -> str:
    cleaned = (title or "").strip()
    if cleaned:
        return cleaned
    return url.strip()


class BookmarkService(BaseService):
    def list_bookmarks(
        self,
        tag_slug: str | None = None,
        category_slug: str | None = None,
        query: str | None = None,
        unlocked_ids: set[str] | None = None,
    ) -> list[BookmarkListItem]:
        with self.read_session() as db:
            bookmarks = BookmarkRepository(db).list_public(
                tag_slug=tag_slug,
                category_slug=category_slug,
                query=query,
            )

        unlocked = unlocked_ids or set()
        items: list[BookmarkListItem] = []
        for bookmark in bookmarks:
            is_unlocked = str(bookmark.id) in unlocked
            if bookmark.is_private and not is_unlocked:
                items.append(
                    BookmarkListItem(
                        id=bookmark.id,
                        title=bookmark.title,
                        is_private=True,
                        requires_unlock=True,
                        category_slug=bookmark.category.slug if bookmark.category else None,
                        category_name=bookmark.category.name if bookmark.category else None,
                        tags=[TagBrief.model_validate(t) for t in bookmark.tags],
                    )
                )
                continue
            items.append(
                BookmarkListItem(
                    id=bookmark.id,
                    title=bookmark.title,
                    url=bookmark.url,
                    description=bookmark.description,
                    favicon_url=bookmark.favicon_url,
                    is_private=bookmark.is_private,
                    category_slug=bookmark.category.slug if bookmark.category else None,
                    category_name=bookmark.category.name if bookmark.category else None,
                    tags=[TagBrief.model_validate(t) for t in bookmark.tags],
                )
            )
        return items

    def quick_add_bookmark(self, url: str) -> UUID:
        cleaned = url.strip()
        if not cleaned:
            raise ValueError("URL 不能为空")
        return self.save_bookmark(SaveBookmarkRequest(url=cleaned))

    def import_bookmarks_from_text(self, text: str) -> dict[str, int | list[str]]:
        lines = text.replace("\r\n", "\n").replace("\r", "\n").split("\n")
        imported = 0
        skipped = 0
        errors: list[str] = []

        for line in lines:
            raw = line.strip()
            if not raw or raw.startswith("#"):
                skipped += 1
                continue

            url = raw if "://" in raw else f"https://{raw}"
            try:
                self.quick_add_bookmark(url)
                imported += 1
            except ValueError as exc:
                errors.append(f"{raw}: {exc}")

        return {"imported": imported, "skipped": skipped, "errors": errors}

    def list_categories_for_admin(self) -> list[dict]:
        with self.read_session() as db:
            categories = BookmarkRepository(db).list_categories()
        return [
            {
                "id": str(c.id),
                "name": c.name,
                "slug": c.slug,
            }
            for c in categories
        ]

    def get_bookmark_for_admin(self, bookmark_id: UUID) -> AdminBookmarkDetail | None:
        with self.read_session() as db:
            bookmark = BookmarkRepository(db).get_by_id(bookmark_id)

        if not bookmark:
            return None

        tags = [TagBrief.model_validate(t) for t in bookmark.tags]
        return AdminBookmarkDetail(
            id=bookmark.id,
            title=bookmark.title,
            url=bookmark.url,
            description=bookmark.description,
            favicon_url=bookmark.favicon_url,
            is_private=bookmark.is_private,
            category_id=bookmark.category_id,
            tag_ids=[t.id for t in bookmark.tags],
            tags=tags,
        )

    def list_bookmarks_for_admin(
        self,
        category_id: UUID | None = None,
    ) -> list[AdminBookmarkListItem]:
        with self.read_session() as db:
            bookmarks = BookmarkRepository(db).list_for_admin(category_id)

        return [
            AdminBookmarkListItem(
                id=b.id,
                title=b.title,
                url=b.url,
                description=b.description,
                is_private=b.is_private,
                category_name=b.category.name if b.category else None,
                tags=[TagBrief.model_validate(t) for t in b.tags],
            )
            for b in bookmarks
        ]

    def save_bookmark(self, body: SaveBookmarkRequest) -> UUID:
        with self.session_scope() as db:
            bookmark_repo = BookmarkRepository(db)
            tag_repo = TagRepository(db)

            if body.id:
                bookmark = bookmark_repo.get_by_id(body.id)
                if not bookmark:
                    raise ValueError("收藏不存在")
            else:
                bookmark = Bookmark()

            password_hash = apply_private_password(
                is_private=body.is_private,
                access_password=body.access_password,
                current_hash=bookmark.access_password_hash if body.id else None,
            )

            url = body.url.strip()
            if not url:
                raise ValueError("URL 不能为空")

            bookmark.title = resolve_bookmark_title(body.title, url)
            bookmark.url = url
            bookmark.description = body.description
            bookmark.favicon_url = body.favicon_url
            bookmark.is_private = body.is_private
            bookmark.access_password_hash = password_hash
            bookmark.category_id = body.category_id
            bookmark.updated_at = utc_now()
            bookmark.tags = tag_repo.resolve_tags(body.tag_ids, body.tag_names)
            bookmark_repo.save(bookmark)
            return bookmark.id

    def delete_bookmark(self, bookmark_id: UUID) -> None:
        with self.session_scope() as db:
            if not BookmarkRepository(db).delete(bookmark_id):
                raise ValueError("收藏不存在")
