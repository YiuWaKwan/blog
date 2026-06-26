from uuid import UUID

from sqlalchemy import func, or_, select
from sqlalchemy.orm import Session, selectinload

from app.models.note import Note, NoteCategory
from app.models.tag import Tag
from app.repositories.base_repository import BaseRepository
from app.schemas.page import PageQuery
from app.schemas.queries.admin import AdminNoteListQuery


class NoteRepository(BaseRepository):
    def list_published(
        self,
        query: PageQuery,
        tag_slug: str | None = None,
        category_slug: str | None = None,
    ) -> tuple[list[Note], int]:
        stmt = (
            select(Note)
            .where(Note.is_published.is_(True))
            .options(
                selectinload(Note.tags),
                selectinload(Note.category),
            )
        )

        if tag_slug:
            stmt = stmt.join(Note.tags).where(Tag.slug == tag_slug)
        if category_slug:
            stmt = stmt.join(Note.category).where(NoteCategory.slug == category_slug)

        count_query = select(func.count()).select_from(stmt.subquery())
        total = self.db.scalar(count_query) or 0

        items = self.db.scalars(
            stmt.order_by(Note.published_at.desc(), Note.sort_order)
            .offset(query.offset)
            .limit(query.limit)
        ).unique().all()

        return list(items), total

    def search_published(self, keyword: str, limit: int = 10) -> list[Note]:
        pattern = f"%{keyword}%"
        return list(
            self.db.scalars(
                select(Note)
                .where(
                    Note.is_published.is_(True),
                    Note.is_private.is_(False),
                    or_(
                        Note.title.ilike(pattern),
                        Note.excerpt.ilike(pattern),
                        Note.content.ilike(pattern),
                    ),
                )
                .options(
                    selectinload(Note.tags),
                    selectinload(Note.category),
                )
                .order_by(Note.published_at.desc())
                .limit(limit)
            ).unique().all()
        )

    def get_by_slug(self, slug: str) -> Note | None:
        return self.db.scalars(
            select(Note)
            .where(Note.slug == slug, Note.is_published.is_(True))
            .options(
                selectinload(Note.tags),
                selectinload(Note.category),
            )
        ).first()

    def get_by_id(self, note_id: UUID) -> Note | None:
        return self.db.scalars(
            select(Note)
            .where(Note.id == note_id)
            .options(
                selectinload(Note.tags),
                selectinload(Note.category),
            )
        ).first()

    def list_for_admin(self, query: AdminNoteListQuery) -> tuple[list[Note], int]:
        stmt = select(Note).options(
            selectinload(Note.tags),
            selectinload(Note.category),
        )

        if query.keyword:
            stmt = stmt.where(Note.title.ilike(f"%{query.keyword}%"))

        count_query = select(func.count()).select_from(stmt.subquery())
        total = self.db.scalar(count_query) or 0

        items = self.db.scalars(
            stmt.order_by(Note.updated_at.desc())
            .offset(query.offset)
            .limit(query.limit)
        ).unique().all()

        return list(items), total

    def count_all(self) -> int:
        return self.db.scalar(select(func.count()).select_from(Note)) or 0

    def list_by_tag_slug(
        self,
        tag_slug: str,
        content_type: str = "note",
    ) -> list[Note]:
        _ = content_type
        return list(
            self.db.scalars(
                select(Note)
                .join(Note.tags)
                .where(Tag.slug == tag_slug, Note.is_published.is_(True))
                .options(selectinload(Note.tags))
                .order_by(Note.published_at.desc())
            ).unique().all()
        )

    def slug_exists(self, slug: str, exclude_id: UUID | None = None) -> bool:
        stmt = select(Note.id).where(Note.slug == slug)
        if exclude_id:
            stmt = stmt.where(Note.id != exclude_id)
        return self.db.scalar(stmt) is not None

    def save(self, note: Note) -> Note:
        self.db.add(note)
        self.db.flush()
        return note

    def delete(self, note_id: UUID) -> bool:
        note = self.get_by_id(note_id)
        if not note:
            return False
        self.db.delete(note)
        return True
