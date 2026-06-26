from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.orm import selectinload

from app.models.bookmark import Bookmark, BookmarkCategory
from app.models.tag import Tag
from app.repositories.base_repository import BaseRepository


class BookmarkRepository(BaseRepository):
    def list_public(
        self,
        tag_slug: str | None = None,
        category_slug: str | None = None,
    ) -> list[Bookmark]:
        stmt = select(Bookmark).options(
            selectinload(Bookmark.tags),
            selectinload(Bookmark.category),
        )

        if tag_slug:
            stmt = stmt.join(Bookmark.tags).where(Tag.slug == tag_slug)
        if category_slug:
            stmt = stmt.join(Bookmark.category).where(
                BookmarkCategory.slug == category_slug
            )

        return list(
            self.db.scalars(
                stmt.order_by(Bookmark.sort_order, Bookmark.title)
            ).unique().all()
        )

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
        if category_id:
            stmt = stmt.where(Bookmark.category_id == category_id)

        return list(
            self.db.scalars(
                stmt.order_by(Bookmark.sort_order, Bookmark.title)
            ).unique().all()
        )

    def count_all(self) -> int:
        return self.db.scalar(select(func.count()).select_from(Bookmark)) or 0

    def list_by_tag_slug(self, tag_slug: str) -> list[Bookmark]:
        return list(
            self.db.scalars(
                select(Bookmark)
                .join(Bookmark.tags)
                .where(Tag.slug == tag_slug)
                .options(selectinload(Bookmark.tags))
                .order_by(Bookmark.sort_order, Bookmark.title)
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

    def delete(self, bookmark_id: UUID) -> bool:
        bookmark = self.get_by_id(bookmark_id)
        if not bookmark:
            return False
        self.db.delete(bookmark)
        return True
