from uuid import UUID

from app.core.datetime_utils import utc_now
from app.models.blog_post import BlogPost
from app.repositories.bookmark_repository import BookmarkRepository
from app.repositories.note_repository import NoteRepository
from app.repositories.post_repository import PostRepository
from app.repositories.tag_repository import TagRepository
from app.schemas.admin import AdminPostDetail, AdminPostListItem, DashboardData
from app.schemas.common import PageData, TagBrief, TagWithStats
from app.schemas.post import PostDetail, PostDetailResult, PostListItem
from app.schemas.queries.admin import AdminPostListQuery
from app.schemas.queries.post import PostListQuery
from app.schemas.requests.admin_post import SavePostRequest
from app.services.base_service import BaseService
from app.services.content_helpers import (
    apply_private_password,
    ensure_unique_slug,
    estimate_reading_time,
)


class PostService(BaseService):
    """博客业务 Service — 通过 DatabaseService 连接池访问数据库。"""

    def list_posts(self, query: PostListQuery) -> PageData[PostListItem]:
        with self.read_session() as db:
            repo = PostRepository(db)
            posts, total = repo.list_published(query, tag_slug=query.tag)

        items = [
            PostListItem(
                id=p.id,
                title=p.title,
                slug=p.slug,
                excerpt=p.excerpt,
                cover_image_url=p.cover_image_url,
                published_at=p.published_at,
                reading_time_minutes=p.reading_time_minutes,
                is_private=p.is_private,
                tags=[TagBrief.model_validate(t) for t in p.tags],
            )
            for p in posts
        ]

        return PageData(
            list=items,
            total=total,
            page=query.page,
            limit=query.limit,
        )

    def get_post_by_slug(
        self,
        slug: str,
        unlocked_ids: set[str] | None = None,
    ) -> PostDetailResult:
        with self.read_session() as db:
            post = PostRepository(db).get_by_slug(slug)

        if not post:
            return PostDetailResult()

        if post.is_private:
            unlocked = unlocked_ids or set()
            if str(post.id) not in unlocked:
                return PostDetailResult(requires_unlock=True, post_id=post.id)

        detail = PostDetail(
            id=post.id,
            title=post.title,
            slug=post.slug,
            excerpt=post.excerpt,
            content=post.content,
            cover_image_url=post.cover_image_url,
            published_at=post.published_at,
            reading_time_minutes=post.reading_time_minutes,
            is_private=post.is_private,
            view_count=post.view_count,
            tags=[TagBrief.model_validate(t) for t in post.tags],
        )
        return PostDetailResult(detail=detail)

    def get_dashboard_stats(self) -> DashboardData:
        with self.read_session() as db:
            post_repo = PostRepository(db)
            note_repo = NoteRepository(db)
            bookmark_repo = BookmarkRepository(db)
            tag_repo = TagRepository(db)

            top_tags = [
                TagWithStats.model_validate(row)
                for row in tag_repo.list_for_admin(sort="total_count")[:10]
            ]

            return DashboardData(
                posts=post_repo.count_all(),
                notes=note_repo.count_all(),
                bookmarks=bookmark_repo.count_all(),
                tags=tag_repo.count_all(),
                top_tags=top_tags,
            )

    def list_posts_for_admin(self, query: AdminPostListQuery) -> PageData[AdminPostListItem]:
        with self.read_session() as db:
            posts, total = PostRepository(db).list_for_admin(query)

        items = [
            AdminPostListItem(
                id=p.id,
                title=p.title,
                slug=p.slug,
                is_published=p.is_published,
                is_private=p.is_private,
                published_at=p.published_at,
                updated_at=p.updated_at,
                tags=[TagBrief.model_validate(t) for t in p.tags],
            )
            for p in posts
        ]
        return PageData(list=items, total=total, page=query.page, limit=query.limit)

    def get_post_for_admin(self, post_id: UUID) -> AdminPostDetail | None:
        with self.read_session() as db:
            post = PostRepository(db).get_by_id(post_id)

        if not post:
            return None

        tags = [TagBrief.model_validate(t) for t in post.tags]
        return AdminPostDetail(
            id=post.id,
            title=post.title,
            slug=post.slug,
            excerpt=post.excerpt,
            content=post.content,
            cover_image_url=post.cover_image_url,
            is_published=post.is_published,
            is_private=post.is_private,
            tag_ids=[t.id for t in post.tags],
            tags=tags,
        )

    def save_post(self, body: SavePostRequest) -> UUID:
        with self.session_scope() as db:
            post_repo = PostRepository(db)
            tag_repo = TagRepository(db)

            if body.id:
                post = post_repo.get_by_id(body.id)
                if not post:
                    raise ValueError("文章不存在")
            else:
                post = BlogPost()

            slug = ensure_unique_slug(
                body.slug or body.title,
                post_repo.slug_exists,
                body.id,
            )

            password_hash = apply_private_password(
                is_private=body.is_private,
                access_password=body.access_password,
                current_hash=post.access_password_hash if body.id else None,
            )

            was_published = post.is_published if body.id else False
            post.title = body.title
            post.slug = slug
            post.excerpt = body.excerpt
            post.content = body.content
            post.cover_image_url = body.cover_image_url
            post.is_published = body.is_published
            post.is_private = body.is_private
            post.access_password_hash = password_hash
            post.reading_time_minutes = estimate_reading_time(body.content)
            post.updated_at = utc_now()

            if body.is_published and not was_published:
                post.published_at = utc_now()
            elif not body.is_published:
                post.published_at = None

            post.tags = tag_repo.resolve_tags(body.tag_ids, body.tag_names)
            post_repo.save(post)
            return post.id

    def delete_post(self, post_id: UUID) -> None:
        with self.session_scope() as db:
            if not PostRepository(db).delete(post_id):
                raise ValueError("文章不存在")
