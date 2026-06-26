import uuid
from datetime import datetime

from app.core.datetime_utils import utc_now

from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, SmallInteger, String, Text, Uuid
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class BlogPost(Base):
    __tablename__ = "blog_posts"

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    slug: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
    excerpt: Mapped[str | None] = mapped_column(Text)
    content: Mapped[str] = mapped_column(Text, nullable=False, default="")
    cover_image_url: Mapped[str | None] = mapped_column(String(512))
    is_published: Mapped[bool] = mapped_column(Boolean, default=False)
    is_private: Mapped[bool] = mapped_column(Boolean, default=False)
    access_password_hash: Mapped[str | None] = mapped_column(String(255))
    reading_time_minutes: Mapped[int | None] = mapped_column(SmallInteger, default=0)
    view_count: Mapped[int] = mapped_column(Integer, default=0)
    author_id: Mapped[uuid.UUID | None] = mapped_column(Uuid, ForeignKey("admin_users.id"))
    published_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now)

    tags: Mapped[list["Tag"]] = relationship(
        secondary="blog_post_tags",
        back_populates="posts",
    )


from app.models.tag import Tag  # noqa: E402, F401
