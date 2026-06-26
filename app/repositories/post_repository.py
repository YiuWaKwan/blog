from uuid import UUID

from sqlalchemy import func, or_, select
from sqlalchemy.orm import selectinload

from app.models.blog_post import BlogPost
from app.models.tag import Tag
from app.repositories.base_repository import BaseRepository
from app.schemas.page import PageQuery
from app.schemas.queries.admin import AdminPostListQuery


class PostRepository(BaseRepository):
    """
    数据访问层 — SQLAlchemy ORM（≈ JPA Repository）。

    手写 SQL（≈ MyBatis）示例::
        from sqlalchemy import text
        self.db.execute(text("SELECT * FROM blog_posts WHERE slug = :slug"), {"slug": slug})
    """
    def list_published(
        self,
        query: PageQuery,
        tag_slug: str | None = None,
    ) -> tuple[list[BlogPost], int]:
        stmt = (
            select(BlogPost)
            .where(BlogPost.is_published.is_(True))
            .options(selectinload(BlogPost.tags))
        )

        if tag_slug:
            stmt = stmt.join(BlogPost.tags).where(Tag.slug == tag_slug)

        count_query = select(func.count()).select_from(stmt.subquery())
        total = self.db.scalar(count_query) or 0

        items = self.db.scalars(
            stmt.order_by(BlogPost.published_at.desc())
            .offset(query.offset)
            .limit(query.limit)
        ).unique().all()

        return list(items), total

    def search_published(self, keyword: str, limit: int = 10) -> list[BlogPost]:
        pattern = f"%{keyword}%"
        return list(
            self.db.scalars(
                select(BlogPost)
                .where(
                    BlogPost.is_published.is_(True),
                    BlogPost.is_private.is_(False),
                    or_(
                        BlogPost.title.ilike(pattern),
                        BlogPost.excerpt.ilike(pattern),
                        BlogPost.content.ilike(pattern),
                    ),
                )
                .options(selectinload(BlogPost.tags))
                .order_by(BlogPost.published_at.desc())
                .limit(limit)
            ).unique().all()
        )

    def get_by_slug(self, slug: str) -> BlogPost | None:
        return self.db.scalars(
            select(BlogPost)
            .where(BlogPost.slug == slug, BlogPost.is_published.is_(True))
            .options(selectinload(BlogPost.tags))
        ).first()

    def get_by_id(self, post_id: UUID) -> BlogPost | None:
        return self.db.scalars(
            select(BlogPost)
            .where(BlogPost.id == post_id)
            .options(selectinload(BlogPost.tags))
        ).first()

    def list_for_admin(self, query: AdminPostListQuery) -> tuple[list[BlogPost], int]:
        stmt = select(BlogPost).options(selectinload(BlogPost.tags))

        if query.keyword:
            stmt = stmt.where(BlogPost.title.ilike(f"%{query.keyword}%"))

        count_query = select(func.count()).select_from(stmt.subquery())
        total = self.db.scalar(count_query) or 0

        items = self.db.scalars(
            stmt.order_by(BlogPost.updated_at.desc())
            .offset(query.offset)
            .limit(query.limit)
        ).unique().all()

        return list(items), total

    def count_all(self) -> int:
        return self.db.scalar(select(func.count()).select_from(BlogPost)) or 0

    def list_by_tag_slug(self, tag_slug: str) -> list[BlogPost]:
        return list(
            self.db.scalars(
                select(BlogPost)
                .join(BlogPost.tags)
                .where(Tag.slug == tag_slug, BlogPost.is_published.is_(True))
                .options(selectinload(BlogPost.tags))
                .order_by(BlogPost.published_at.desc())
            ).unique().all()
        )

    def slug_exists(self, slug: str, exclude_id: UUID | None = None) -> bool:
        stmt = select(BlogPost.id).where(BlogPost.slug == slug)
        if exclude_id:
            stmt = stmt.where(BlogPost.id != exclude_id)
        return self.db.scalar(stmt) is not None

    def save(self, post: BlogPost) -> BlogPost:
        self.db.add(post)
        self.db.flush()
        return post

    def delete(self, post_id: UUID) -> bool:
        post = self.get_by_id(post_id)
        if not post:
            return False
        self.db.delete(post)
        return True
