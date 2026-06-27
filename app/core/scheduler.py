"""应用内定时任务调度。"""

import logging

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger

from app.core.config import settings
from app.services.bookmark_url_check_service import BookmarkUrlCheckService

logger = logging.getLogger(__name__)

scheduler = AsyncIOScheduler(timezone=settings.scheduler_timezone)


def run_bookmark_url_check() -> None:
    try:
        BookmarkUrlCheckService().check_all()
    except Exception:
        logger.exception("Bookmark URL check job failed")


def start_scheduler() -> None:
    if not settings.bookmark_url_check_enabled:
        return

    scheduler.add_job(
        run_bookmark_url_check,
        CronTrigger(minute=1,second=0),
        id="bookmark_url_check",
        replace_existing=True,
        misfire_grace_time=3600,
    )
    scheduler.start()
    logger.info(
        "Bookmark URL check scheduled daily at %02d:00 (%s)",
        settings.bookmark_url_check_hour,
        settings.scheduler_timezone,
    )


def shutdown_scheduler() -> None:
    if scheduler.running:
        scheduler.shutdown(wait=False)
