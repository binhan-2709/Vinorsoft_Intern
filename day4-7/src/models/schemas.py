"""
src/models/schemas.py — Pydantic schemas cho API request/response.

Day 4: Validate input và serialize output tách biệt với ORM models.
"""
from datetime import datetime

from pydantic import BaseModel, EmailStr, Field

from src.models.orm import PostStatus, UserRole


# ══════════════════════════════════════════════════════════════════════
# AUTH SCHEMAS
# ══════════════════════════════════════════════════════════════════════

class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class TokenPayload(BaseModel):
    sub: str          # user id
    role: str
    exp: int


# ══════════════════════════════════════════════════════════════════════
# USER SCHEMAS
# ══════════════════════════════════════════════════════════════════════

class UserRegister(BaseModel):
    username: str = Field(..., min_length=3, max_length=50)
    email: EmailStr
    password: str = Field(..., min_length=6)
    full_name: str | None = Field(None, max_length=100)

    model_config = {
        "json_schema_extra": {
            "example": {
                "username": "dangbinhan",
                "email": "binhan27092005@gmail.com",
                "password": "123456",
                "full_name": "Dang Binh An",
            }
        }
    }


class UserLogin(BaseModel):
    username: str
    password: str


class UserResponse(BaseModel):
    id: int
    username: str
    email: str
    full_name: str | None
    role: UserRole
    is_active: bool
    created_at: datetime

    model_config = {"from_attributes": True}


# ══════════════════════════════════════════════════════════════════════
# POST SCHEMAS  (Day 4 — chỉ title và content khi tạo)
# ══════════════════════════════════════════════════════════════════════

class PostCreate(BaseModel):
    """Người dùng chỉ cần điền title và content."""
    title: str = Field(..., min_length=3, max_length=200)
    content: str = Field(..., min_length=10)

    model_config = {
        "json_schema_extra": {
            "example": {
                "title": "Đề tài bài viết của bạn...",
                "content": "Nội dung bài viết của bạn",
            }
        }
    }


class PostUpdate(BaseModel):
    """Partial update — chỉ gửi field muốn thay đổi."""
    title: str | None = Field(None, min_length=3, max_length=200)
    content: str | None = Field(None, min_length=10)
    status: PostStatus | None = None


class PostResponse(BaseModel):
    id: int
    title: str
    content: str
    status: PostStatus
    views: int
    author_id: int
    author_name: str | None = None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class PaginatedPosts(BaseModel):
    total: int
    page: int
    page_size: int
    posts: list[PostResponse]


class MessageResponse(BaseModel):
    message: str