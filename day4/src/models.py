from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
from enum import Enum


class Category(str, Enum):
    tech = "tech"
    lifestyle = "lifestyle"
    travel = "travel"
    food = "food"
    other = "other"


# ── Input schemas ─────────────────────────────────────────────────────

class PostCreate(BaseModel):
    title: str = Field(..., min_length=3, max_length=100, description="Tiêu đề bài viết")
    content: str = Field(..., min_length=10, description="Nội dung bài viết")
    category: Category = Category.other
    tags: list[str] = Field(default=[], description="Danh sách tag")
    published: bool = False

    model_config = {
        "json_schema_extra": {
            "example": {
                "title": "Nhập tiêu đề",
                "content": "Nhập nội dung",
                "category": "tech",
                "tags": ["python", "fastapi", "backend"],
                "published": True,
            }
        }
    }


class PostUpdate(BaseModel):
    """Partial update — chỉ gửi field cần thay đổi (PATCH)."""
    title: Optional[str] = Field(None, min_length=3, max_length=100)
    content: Optional[str] = Field(None, min_length=10)
    category: Optional[Category] = None
    tags: Optional[list[str]] = None
    published: Optional[bool] = None


# ── Output schemas ────────────────────────────────────────────────────

class PostResponse(BaseModel):
    id: int
    title: str
    content: str
    category: Category
    tags: list[str]
    published: bool
    author: str
    created_at: datetime
    updated_at: datetime
    views: int


class PostSummary(BaseModel):
    """Phiên bản rút gọn — dùng trong danh sách."""
    id: int
    title: str
    category: Category
    tags: list[str]
    published: bool
    author: str
    created_at: datetime
    views: int


class PaginatedPosts(BaseModel):
    total: int
    page: int
    page_size: int
    posts: list[PostSummary]


class MessageResponse(BaseModel):
    message: str