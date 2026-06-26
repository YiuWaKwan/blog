import secrets
from datetime import timedelta
from uuid import UUID

from sqlalchemy import delete, select
from sqlalchemy.orm import selectinload

from app.core.datetime_utils import utc_now
from app.models.content_unlock import ContentUnlock
from app.repositories.base_repository import BaseRepository


class UnlockRepository(BaseRepository):
    def create_unlock(
        self,
        resource_type: str,
        resource_id: UUID,
        expires_hours: int = 24,
    ) -> ContentUnlock:
        unlock = ContentUnlock(
            resource_type=resource_type,
            resource_id=resource_id,
            session_token=secrets.token_urlsafe(32),
            expires_at=utc_now() + timedelta(hours=expires_hours),
        )
        self.db.add(unlock)
        self.db.flush()
        return unlock

    def get_valid_unlocks(self, tokens: list[str]) -> list[ContentUnlock]:
        if not tokens:
            return []
        now = utc_now()
        return list(
            self.db.scalars(
                select(ContentUnlock).where(
                    ContentUnlock.session_token.in_(tokens),
                    ContentUnlock.expires_at > now,
                )
            ).all()
        )

    def cleanup_expired(self) -> None:
        now = utc_now()
        self.db.execute(
            delete(ContentUnlock).where(ContentUnlock.expires_at <= now)
        )
