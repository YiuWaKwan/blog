"""收藏 URL 定时健康检查。"""

import logging
from uuid import UUID

from app.core.config import settings
from app.core.datetime_utils import utc_now
from app.core.url_fetcher import FetchOutcome, fetch_url_best_effort
from app.repositories.bookmark_repository import BookmarkRepository
from app.services.base_service import BaseService

logger = logging.getLogger(__name__)


class BookmarkUrlCheckService(BaseService):
    def check_all(self) -> dict[str, int]:
        with self.read_session() as db:
            bookmarks = BookmarkRepository(db).list_active_for_url_check()

        checked = 0
        updated = 0
        failed = 0
        blocked = 0
        deleted = 0

        fail_threshold = settings.bookmark_url_check_fail_days
        timeout = settings.bookmark_url_check_timeout_seconds
        proxy = settings.bookmark_url_check_proxy or None

        for bookmark in bookmarks:
            checked += 1
            result = fetch_url_best_effort(
                bookmark.url,
                timeout=timeout,
                proxy=proxy,
            )

            if result.outcome is FetchOutcome.SUCCESS:
                if self._mark_success(bookmark.id, result.title):
                    updated += 1
                continue

            if result.outcome is FetchOutcome.BLOCKED:
                blocked += 1
                self._mark_blocked(bookmark.id)
                logger.info(
                    "Bookmark URL check blocked for %s via %s: %s",
                    bookmark.url,
                    result.strategy,
                    result.detail,
                )
                continue

            failed += 1
            logger.warning(
                "Bookmark URL check failed for %s via %s: %s",
                bookmark.url,
                result.strategy,
                result.detail,
            )
            if self._mark_failure(bookmark.id, fail_threshold):
                deleted += 1

        summary = {
            "checked": checked,
            "updated": updated,
            "blocked": blocked,
            "failed": failed,
            "deleted": deleted,
        }
        logger.info("Bookmark URL check finished: %s", summary)
        return summary

    def _mark_success(self, bookmark_id: UUID, page_title: str | None) -> bool:
        now = utc_now()
        with self.session_scope() as db:
            bookmark = BookmarkRepository(db).get_by_id(bookmark_id)
            if not bookmark or bookmark.deleted_at is not None:
                return False

            bookmark.url_check_fail_days = 0
            bookmark.last_url_check_at = now
            title_changed = False

            if page_title and page_title != bookmark.title:
                bookmark.title = page_title
                title_changed = True

            bookmark.updated_at = now
            BookmarkRepository(db).save(bookmark)
            return title_changed

    def _mark_blocked(self, bookmark_id: UUID) -> None:
        now = utc_now()
        with self.session_scope() as db:
            bookmark = BookmarkRepository(db).get_by_id(bookmark_id)
            if not bookmark or bookmark.deleted_at is not None:
                return

            bookmark.last_url_check_at = now
            BookmarkRepository(db).save(bookmark)

    def _mark_failure(self, bookmark_id: UUID, fail_threshold: int) -> bool:
        now = utc_now()
        with self.session_scope() as db:
            repo = BookmarkRepository(db)
            bookmark = repo.get_by_id(bookmark_id)
            if not bookmark or bookmark.deleted_at is not None:
                return False

            bookmark.url_check_fail_days += 1
            bookmark.last_url_check_at = now
            bookmark.updated_at = now

            if bookmark.url_check_fail_days >= fail_threshold:
                bookmark.deleted_at = now
                repo.save(bookmark)
                return True

            repo.save(bookmark)
            return False
