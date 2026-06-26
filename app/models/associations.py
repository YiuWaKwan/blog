from sqlalchemy import Column, ForeignKey, Table, Uuid

from app.core.database import Base

blog_post_tags = Table(
    "blog_post_tags",
    Base.metadata,
    Column("post_id", Uuid, ForeignKey("blog_posts.id", ondelete="CASCADE"), primary_key=True),
    Column("tag_id", Uuid, ForeignKey("tags.id", ondelete="CASCADE"), primary_key=True),
)

note_tags = Table(
    "note_tags",
    Base.metadata,
    Column("note_id", Uuid, ForeignKey("notes.id", ondelete="CASCADE"), primary_key=True),
    Column("tag_id", Uuid, ForeignKey("tags.id", ondelete="CASCADE"), primary_key=True),
)

bookmark_tags = Table(
    "bookmark_tags",
    Base.metadata,
    Column("bookmark_id", Uuid, ForeignKey("bookmarks.id", ondelete="CASCADE"), primary_key=True),
    Column("tag_id", Uuid, ForeignKey("tags.id", ondelete="CASCADE"), primary_key=True),
)
