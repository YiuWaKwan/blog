from uuid import UUID

from sqlalchemy import func, select, update
from sqlalchemy.orm import selectinload
from sqlalchemy.sql import Select

from app.core.datetime_utils import utc_now
from app.models.bookmark import Bookmark, BookmarkCategory
from app.models.tag import Tag
from app.repositories.base_repository import BaseRepository


class BookmarkRepository(BaseRepository):
    @staticmethod
    def _active_only(stmt: Select) -> Select:
        return stmt.where(Bookmark.deleted_at.is_(None))

    def list_public(
        self,
        tag_slug: str | None = None,
        category_slug: str | None = None,
        query: str | None = None,
    ) -> list[Bookmark]:
        stmt = select(Bookmark).options(
            selectinload(Bookmark.tags),
            selectinload(Bookmark.category),
        )
        stmt = self._active_only(stmt)

        if tag_slug:
            stmt = stmt.join(Bookmark.tags).where(Tag.slug == tag_slug)
        if category_slug:
            stmt = stmt.join(Bookmark.category).where(
                BookmarkCategory.slug == category_slug
            )
        if query:
            pattern = f"%{query.strip()}%"
            stmt = stmt.where(
                Bookmark.title.ilike(pattern) | Bookmark.url.ilike(pattern)
            )

        return list(
            self.db.scalars(
                stmt.order_by(
                    Bookmark.visit_count.desc(),
                    Bookmark.sort_order,
                    Bookmark.title,
                )
            ).unique().all()
        )

    def list_active_for_url_check(self) -> list[Bookmark]:
        return list(
            self.db.scalars(
                self._active_only(select(Bookmark)).order_by(Bookmark.created_at)
            ).all()
        )

    def increment_visit_count(self, bookmark_id: UUID) -> bool:
        result = self.db.execute(
            update(Bookmark)
            .where(Bookmark.id == bookmark_id, Bookmark.deleted_at.is_(None))
            .values(visit_count=Bookmark.visit_count + 1)
        )
        return result.rowcount > 0

    def get_by_id(self, bookmark_id: UUID) -> Bookmark | None:
        return self.db.scalars(
            select(Bookmark)
            .where(Bookmark.id == bookmark_id)
            .options(
                selectinload(Bookmark.tags),
                selectinload(Bookmark.category),
            )
        ).first()

    def list_for_admin(
        self,
        category_id: UUID | None = None,
    ) -> list[Bookmark]:
        stmt = select(Bookmark).options(
            selectinload(Bookmark.tags),
            selectinload(Bookmark.category),
        )
        stmt = self._active_only(stmt)
        if category_id:
            stmt = stmt.where(Bookmark.category_id == category_id)

        return list(
            self.db.scalars(
                stmt.order_by(Bookmark.sort_order, Bookmark.title)
            ).unique().all()
        )

    def count_all(self) -> int:
        return (
            self.db.scalar(
                self._active_only(select(func.count()).select_from(Bookmark))
            )
            or 0
        )

    def list_by_tag_slug(self, tag_slug: str) -> list[Bookmark]:
        return list(
            self.db.scalars(
                self._active_only(
                    select(Bookmark)
                    .join(Bookmark.tags)
                    .where(Tag.slug == tag_slug)
                    .options(selectinload(Bookmark.tags))
                    .order_by(Bookmark.sort_order, Bookmark.title)
                )
            ).unique().all()
        )

    def list_categories(self) -> list[BookmarkCategory]:
        return list(
            self.db.scalars(
                select(BookmarkCategory).order_by(
                    BookmarkCategory.sort_order,
                    BookmarkCategory.name,
                )
            ).all()
        )

    def save(self, bookmark: Bookmark) -> Bookmark:
        self.db.add(bookmark)
        self.db.flush()
        return bookmark

    def soft_delete(self, bookmark_id: UUID) -> bool:
        bookmark = self.get_by_id(bookmark_id)
        if not bookmark or bookmark.deleted_at is not None:
            return False
        bookmark.deleted_at = utc_now()
        bookmark.updated_at = utc_now()
        return True

    def delete(self, bookmark_id: UUID) -> bool:
        bookmark = self.get_by_id(bookmark_id)
        if not bookmark:
            return False
        self.db.delete(bookmark)
        return True
