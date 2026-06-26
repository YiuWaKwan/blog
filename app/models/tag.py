import uuid
from datetime import datetime

from app.core.datetime_utils import utc_now

from sqlalchemy import DateTime, String, Uuid
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class Tag(Base):
    __tablename__ = "tags"

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    name: Mapped[str] = mapped_column(String(64), nullable=False)
    slug: Mapped[str] = mapped_column(String(64), unique=True, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now)

    posts: Mapped[list["BlogPost"]] = relationship(
        secondary="blog_post_tags",
        back_populates="tags",
    )
    notes: Mapped[list["Note"]] = relationship(
        secondary="note_tags",
        back_populates="tags",
    )
    bookmarks: Mapped[list["Bookmark"]] = relationship(
        secondary="bookmark_tags",
        back_populates="tags",
    )


from app.models.blog_post import BlogPost  # noqa: E402, F401
from app.models.bookmark import Bookmark  # noqa: E402, F401
from app.models.note import Note  # noqa: E402, F401
