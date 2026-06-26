from app.repositories.note_repository import NoteRepository
from app.repositories.post_repository import PostRepository
from app.repositories.tag_repository import TagRepository
from app.schemas.search import SearchResultItem
from app.services.base_service import BaseService


class SearchService(BaseService):
    def search(self, keyword: str, limit: int = 20) -> list[SearchResultItem]:
        keyword = keyword.strip()
        if not keyword:
            return []

        per_type = max(limit // 3, 5)

        with self.read_session() as db:
            posts = PostRepository(db).search_published(keyword, per_type)
            notes = NoteRepository(db).search_published(keyword, per_type)
            tags = TagRepository(db).search_by_name(keyword, min(per_type, 10))

        items: list[SearchResultItem] = []

        for post in posts:
            items.append(
                SearchResultItem(
                    content_type="blog",
                    title=post.title,
                    slug=post.slug,
                    excerpt=post.excerpt,
                    published_at=post.published_at,
                )
            )

        for note in notes:
            items.append(
                SearchResultItem(
                    content_type="note",
                    title=note.title,
                    slug=note.slug,
                    excerpt=note.excerpt,
                    published_at=note.published_at,
                )
            )

        for tag in tags:
            items.append(
                SearchResultItem(
                    content_type="tag",
                    title=tag["name"],
                    slug=tag["slug"],
                    excerpt=f"博客 {tag.get('blog_count', 0)} · 笔记 {tag.get('note_count', 0)}",
                )
            )

        return items[:limit]
