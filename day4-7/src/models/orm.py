"""
src/models/orm.py — SQLAlchemy ORM models (bảng trong database).

Day 5: Thiết kế schema với relationship, index, constraint.
"""
from datetime import datetime
from enum import Enum as PyEnum

from sqlalchemy import (
    Boolean,
    DateTime,
    Enum,
    ForeignKey,
    Index,
    Integer,
    String,
    Text,
    func,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.db.base import Base


class UserRole(str, PyEnum):
    """Role của người dùng — dùng cho phân quyền Day 6."""
    admin = "admin"
    author = "author"
    reader = "reader"


class PostStatus(str, PyEnum):
    draft = "draft"
    published = "published"
    archived = "archived"


# ── User table ────────────────────────────────────────────────────────
class User(Base):
    """Bảng người dùng."""

    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    username: Mapped[str] = mapped_column(String(50), unique=True, nullable=False, index=True)
    email: Mapped[str] = mapped_column(String(255), unique=True, nullable=False, index=True)
    hashed_password: Mapped[str] = mapped_column(String(255), nullable=False)
    full_name: Mapped[str | None] = mapped_column(String(100))
    role: Mapped[UserRole] = mapped_column(
        Enum(UserRole), default=UserRole.author, nullable=False
    )
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False
    )

    # Relationship
    posts: Mapped[list["Post"]] = relationship("Post", back_populates="author", lazy="selectin")

    def __repr__(self) -> str:
        return f"<User id={self.id} username={self.username}>"


# ── Post table ────────────────────────────────────────────────────────
class Post(Base):
    """Bảng bài viết."""

    __tablename__ = "posts"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    status: Mapped[PostStatus] = mapped_column(
        Enum(PostStatus), default=PostStatus.draft, nullable=False
    )
    views: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    author_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False
    )

    # Relationship
    author: Mapped["User"] = relationship("User", back_populates="posts", lazy="selectin")

    # Composite index: lọc theo author + status thường xuyên
    __table_args__ = (
        Index("ix_posts_author_status", "author_id", "status"),
        Index("ix_posts_created_at", "created_at"),
    )

    def __repr__(self) -> str:
        return f"<Post id={self.id} title={self.title!r}>"