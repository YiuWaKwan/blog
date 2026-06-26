from uuid import UUID

from app.core.datetime_utils import utc_now
from app.models.note import Note
from app.repositories.note_repository import NoteRepository
from app.repositories.tag_repository import TagRepository
from app.schemas.admin import AdminNoteDetail, AdminNoteListItem
from app.schemas.common import PageData, TagBrief
from app.schemas.note import NoteDetail, NoteDetailResult, NoteListItem
from app.schemas.queries.admin import AdminNoteListQuery
from app.schemas.queries.note import NoteListQuery
from app.schemas.requests.admin_note import SaveNoteRequest
from app.services.base_service import BaseService
from app.services.content_helpers import (
    apply_private_password,
    ensure_unique_slug,
    estimate_reading_time,
)


class NoteService(BaseService):
    def list_notes(self, query: NoteListQuery) -> PageData[NoteListItem]:
        with self.read_session() as db:
            notes, total = NoteRepository(db).list_published(
                query,
                tag_slug=query.tag,
                category_slug=query.category,
            )

        items = [
            NoteListItem(
                id=n.id,
                title=n.title,
                slug=n.slug,
                excerpt=n.excerpt,
                cover_image_url=n.cover_image_url,
                published_at=n.published_at,
                reading_time_minutes=n.reading_time_minutes,
                is_private=n.is_private,
                category_slug=n.category.slug if n.category else None,
                category_name=n.category.name if n.category else None,
                tags=[TagBrief.model_validate(t) for t in n.tags],
            )
            for n in notes
        ]
        return PageData(list=items, total=total, page=query.page, limit=query.limit)

    def get_note_by_slug(
        self,
        slug: str,
        unlocked_ids: set[str] | None = None,
    ) -> NoteDetailResult:
        with self.read_session() as db:
            note = NoteRepository(db).get_by_slug(slug)

        if not note:
            return NoteDetailResult()

        if note.is_private:
            unlocked = unlocked_ids or set()
            if str(note.id) not in unlocked:
                return NoteDetailResult(requires_unlock=True, note_id=note.id)

        detail = NoteDetail(
            id=note.id,
            title=note.title,
            slug=note.slug,
            excerpt=note.excerpt,
            content=note.content,
            cover_image_url=note.cover_image_url,
            published_at=note.published_at,
            reading_time_minutes=note.reading_time_minutes,
            is_private=note.is_private,
            category_slug=note.category.slug if note.category else None,
            category_name=note.category.name if note.category else None,
            view_count=note.view_count,
            tags=[TagBrief.model_validate(t) for t in note.tags],
        )
        return NoteDetailResult(detail=detail)

    def list_notes_for_admin(self, query: AdminNoteListQuery) -> PageData[AdminNoteListItem]:
        with self.read_session() as db:
            notes, total = NoteRepository(db).list_for_admin(query)

        items = [
            AdminNoteListItem(
                id=n.id,
                title=n.title,
                slug=n.slug,
                is_published=n.is_published,
                is_private=n.is_private,
                published_at=n.published_at,
                updated_at=n.updated_at,
                category_name=n.category.name if n.category else None,
                tags=[TagBrief.model_validate(t) for t in n.tags],
            )
            for n in notes
        ]
        return PageData(list=items, total=total, page=query.page, limit=query.limit)

    def get_note_for_admin(self, note_id: UUID) -> AdminNoteDetail | None:
        with self.read_session() as db:
            note = NoteRepository(db).get_by_id(note_id)

        if not note:
            return None

        tags = [TagBrief.model_validate(t) for t in note.tags]
        return AdminNoteDetail(
            id=note.id,
            title=note.title,
            slug=note.slug,
            excerpt=note.excerpt,
            content=note.content,
            cover_image_url=note.cover_image_url,
            is_published=note.is_published,
            is_private=note.is_private,
            category_id=note.category_id,
            tag_ids=[t.id for t in note.tags],
            tags=tags,
        )

    def save_note(self, body: SaveNoteRequest) -> UUID:
        with self.session_scope() as db:
            note_repo = NoteRepository(db)
            tag_repo = TagRepository(db)

            if body.id:
                note = note_repo.get_by_id(body.id)
                if not note:
                    raise ValueError("笔记不存在")
            else:
                note = Note()

            slug = ensure_unique_slug(
                body.slug or body.title,
                note_repo.slug_exists,
                body.id,
            )

            password_hash = apply_private_password(
                is_private=body.is_private,
                access_password=body.access_password,
                current_hash=note.access_password_hash if body.id else None,
            )

            was_published = note.is_published if body.id else False
            note.title = body.title
            note.slug = slug
            note.excerpt = body.excerpt
            note.content = body.content
            note.cover_image_url = body.cover_image_url
            note.is_published = body.is_published
            note.is_private = body.is_private
            note.access_password_hash = password_hash
            note.category_id = body.category_id
            note.reading_time_minutes = estimate_reading_time(body.content)
            note.updated_at = utc_now()

            if body.is_published and not was_published:
                note.published_at = utc_now()
            elif not body.is_published:
                note.published_at = None

            note.tags = tag_repo.resolve_tags(body.tag_ids, body.tag_names)
            note_repo.save(note)
            return note.id

    def delete_note(self, note_id: UUID) -> None:
        with self.session_scope() as db:
            if not NoteRepository(db).delete(note_id):
                raise ValueError("笔记不存在")
