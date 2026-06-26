from uuid import UUID

from sqlalchemy import func, or_, select, text

from app.core.slug_utils import slugify
from app.models.tag import Tag
from app.repositories.base_repository import BaseRepository


class TagRepository(BaseRepository):
    def list_all(self) -> list[dict]:
        rows = self.db.execute(
            text(
                """
                SELECT id, name, slug, blog_count, note_count, bookmark_count, total_count
                FROM v_tag_stats
                ORDER BY name
                """
            )
        ).mappings()
        return [dict(row) for row in rows]

    def list_for_admin(
        self,
        q: str | None = None,
        sort: str | None = None,
    ) -> list[dict]:
        order_by = "total_count DESC, name"
        if sort == "name":
            order_by = "name"
        elif sort == "blog_count":
            order_by = "blog_count DESC, name"
        elif sort == "note_count":
            order_by = "note_count DESC, name"
        elif sort == "bookmark_count":
            order_by = "bookmark_count DESC, name"

        sql = f"""
            SELECT id, name, slug, created_at,
                   blog_count, note_count, bookmark_count, total_count
            FROM v_tag_stats
            {{where_clause}}
            ORDER BY {order_by}
        """
        params: dict = {}
        where_clause = ""
        if q:
            where_clause = "WHERE name ILIKE :q OR slug ILIKE :q"
            params["q"] = f"%{q}%"

        rows = self.db.execute(
            text(sql.format(where_clause=where_clause)),
            params,
        ).mappings()
        return [dict(row) for row in rows]

    def list_popular(self, limit: int) -> list[dict]:
        rows = self.db.execute(
            text(
                """
                SELECT id, name, slug, blog_count, note_count, bookmark_count, total_count
                FROM v_tag_stats
                WHERE total_count > 0
                ORDER BY total_count DESC, name
                LIMIT :limit
                """
            ),
            {"limit": limit},
        ).mappings()
        return [dict(row) for row in rows]

    def search_by_name(self, keyword: str, limit: int = 10) -> list[dict]:
        rows = self.db.execute(
            text(
                """
                SELECT id, name, slug, blog_count, note_count, bookmark_count, total_count
                FROM v_tag_stats
                WHERE name ILIKE :q OR slug ILIKE :q
                ORDER BY total_count DESC, name
                LIMIT :limit
                """
            ),
            {"q": f"%{keyword}%", "limit": limit},
        ).mappings()
        return [dict(row) for row in rows]

    def get_by_slug(self, slug: str) -> dict | None:
        row = self.db.execute(
            text(
                """
                SELECT id, name, slug, blog_count, note_count, bookmark_count, total_count
                FROM v_tag_stats
                WHERE slug = :slug
                """
            ),
            {"slug": slug},
        ).mappings().first()
        return dict(row) if row else None

    def get_by_id(self, tag_id: UUID) -> Tag | None:
        return self.db.get(Tag, tag_id)

    def get_entity_by_slug(self, slug: str) -> Tag | None:
        return self.db.scalars(select(Tag).where(Tag.slug == slug)).first()

    def count_all(self) -> int:
        return self.db.scalar(select(func.count()).select_from(Tag)) or 0

    def create(self, name: str, slug: str | None = None) -> Tag:
        tag = Tag(name=name, slug=slug or slugify(name))
        self.db.add(tag)
        self.db.flush()
        return tag

    def update(self, tag: Tag, name: str, slug: str | None = None) -> Tag:
        tag.name = name
        tag.slug = slug or slugify(name)
        self.db.flush()
        return tag

    def delete(self, tag_id: UUID) -> bool:
        tag = self.get_by_id(tag_id)
        if not tag:
            return False
        self.db.delete(tag)
        return True

    def resolve_tags(
        self,
        tag_ids: list[UUID],
        tag_names: list[str],
    ) -> list[Tag]:
        tags: list[Tag] = []
        seen: set[UUID] = set()

        if tag_ids:
            found = self.db.scalars(
                select(Tag).where(Tag.id.in_(tag_ids))
            ).all()
            for tag in found:
                if tag.id not in seen:
                    tags.append(tag)
                    seen.add(tag.id)

        for name in tag_names:
            name = name.strip()
            if not name:
                continue
            existing = self.db.scalars(
                select(Tag).where(or_(Tag.name == name, Tag.slug == slugify(name)))
            ).first()
            if existing:
                if existing.id not in seen:
                    tags.append(existing)
                    seen.add(existing.id)
            else:
                created = self.create(name)
                tags.append(created)
                seen.add(created.id)

        return tags
