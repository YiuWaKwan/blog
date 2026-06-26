import uuid
from datetime import datetime

from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, String, Text, Uuid
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base
from app.core.datetime_utils import utc_now


class BookmarkCategory(Base):
    __tablename__ = "bookmark_categories"

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    name: Mapped[str] = mapped_column(String(64), nullable=False)
    slug: Mapped[str] = mapped_column(String(64), unique=True, nullable=False)
    sort_order: Mapped[int] = mapped_column(Integer, default=0)


class Bookmark(Base):
    __tablename__ = "bookmarks"

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    url: Mapped[str] = mapped_column(String(2048), nullable=False)
    description: Mapped[str | None] = mapped_column(Text)
    favicon_url: Mapped[str | None] = mapped_column(String(512))
    category_id: Mapped[uuid.UUID | None] = mapped_column(
        Uuid, ForeignKey("bookmark_categories.id")
    )
    is_private: Mapped[bool] = mapped_column(Boolean, default=False)
    access_password_hash: Mapped[str | None] = mapped_column(String(255))
    sort_order: Mapped[int] = mapped_column(Integer, default=0)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now)

    category: Mapped["BookmarkCategory | None"] = relationship()
    tags: Mapped[list["Tag"]] = relationship(
        secondary="bookmark_tags",
        back_populates="bookmarks",
    )


from app.models.tag import Tag  # noqa: E402, F401
