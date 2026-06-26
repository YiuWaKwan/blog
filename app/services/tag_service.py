from uuid import UUID

from app.repositories.bookmark_repository import BookmarkRepository
from app.repositories.note_repository import NoteRepository
from app.repositories.post_repository import PostRepository
from app.repositories.tag_repository import TagRepository
from app.schemas.admin import AdminTagListItem
from app.schemas.common import TagBrief, TagWithStats
from app.schemas.requests.admin_tag import SaveTagRequest
from app.services.base_service import BaseService


class TagService(BaseService):
    def list_tags(self) -> list[TagWithStats]:
        with self.read_session() as db:
            rows = TagRepository(db).list_all()
        return [TagWithStats.model_validate(row) for row in rows]

    def list_popular(self, limit: int) -> list[TagWithStats]:
        with self.read_session() as db:
            rows = TagRepository(db).list_popular(limit)
        return [TagWithStats.model_validate(row) for row in rows]

    def get_tag_detail(
        self,
        slug: str,
        content_type: str = "all",
        unlocked_bookmark_ids: set[str] | None = None,
    ) -> dict | None:
        with self.read_session() as db:
            tag_repo = TagRepository(db)
            post_repo = PostRepository(db)
            note_repo = NoteRepository(db)
            bookmark_repo = BookmarkRepository(db)

            tag_row = tag_repo.get_by_slug(slug)
            if not tag_row:
                return None

            items: list[dict] = []

            if content_type in ("all", "blog"):
                for post in post_repo.list_by_tag_slug(slug):
                    items.append(
                        {
                            "id": str(post.id),
                            "title": post.title,
                            "slug": post.slug,
                            "content_type": "blog",
                            "published_at": post.published_at.isoformat()
                            if post.published_at
                            else None,
                            "tags": [
                                TagBrief.model_validate(t).model_dump() for t in post.tags
                            ],
                        }
                    )

            if content_type in ("all", "note"):
                for note in note_repo.list_by_tag_slug(slug):
                    items.append(
                        {
                            "id": str(note.id),
                            "title": note.title,
                            "slug": note.slug,
                            "content_type": "note",
                            "published_at": note.published_at.isoformat()
                            if note.published_at
                            else None,
                            "tags": [
                                TagBrief.model_validate(t).model_dump() for t in note.tags
                            ],
                        }
                    )

            if content_type in ("all", "bookmark"):
                unlocked = unlocked_bookmark_ids or set()
                for bookmark in bookmark_repo.list_by_tag_slug(slug):
                    if bookmark.is_private and str(bookmark.id) not in unlocked:
                        items.append(
                            {
                                "id": str(bookmark.id),
                                "title": bookmark.title,
                                "content_type": "bookmark",
                                "requires_unlock": True,
                                "published_at": None,
                                "tags": [
                                    TagBrief.model_validate(t).model_dump()
                                    for t in bookmark.tags
                                ],
                            }
                        )
                        continue
                    items.append(
                        {
                            "id": str(bookmark.id),
                            "title": bookmark.title,
                            "url": bookmark.url,
                            "content_type": "bookmark",
                            "requires_unlock": False,
                            "published_at": None,
                            "tags": [
                                TagBrief.model_validate(t).model_dump()
                                for t in bookmark.tags
                            ],
                        }
                    )

            return {
                "tag": TagWithStats.model_validate(tag_row).model_dump(),
                "items": items,
            }

    def list_for_admin(
        self,
        q: str | None = None,
        sort: str | None = None,
    ) -> list[AdminTagListItem]:
        with self.read_session() as db:
            rows = TagRepository(db).list_for_admin(q, sort)
        return [AdminTagListItem.model_validate(row) for row in rows]

    def get_tag_for_admin(self, tag_id: UUID) -> TagBrief | None:
        with self.read_session() as db:
            tag = TagRepository(db).get_by_id(tag_id)
        if not tag:
            return None
        return TagBrief.model_validate(tag)

    def save_tag(self, body: SaveTagRequest) -> UUID:
        with self.session_scope() as db:
            repo = TagRepository(db)
            if body.id:
                tag = repo.get_by_id(body.id)
                if not tag:
                    raise ValueError("标签不存在")
                repo.update(tag, body.name, body.slug)
                return tag.id

            tag = repo.create(body.name, body.slug)
            return tag.id

    def delete_tag(self, tag_id: UUID) -> None:
        with self.session_scope() as db:
            if not TagRepository(db).delete(tag_id):
                raise ValueError("标签不存在")
