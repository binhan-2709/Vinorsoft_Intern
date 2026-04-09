"""
src/api/v1/posts.py — CRUD endpoints cho bài viết.

Day 4: Path/Query Params, Pydantic schemas.
Day 5: Async DB queries.
Day 6: JWT auth + role-based access.
Day 7: Background tasks khi xem bài viết.
"""
from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, Path, Query, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Annotated

from src.db.session import get_db
from src.deps.auth import get_current_active_user, require_role
from src.models.orm import Post, PostStatus, User, UserRole
from src.models.schemas import (
    MessageResponse,
    PaginatedPosts,
    PostCreate,
    PostResponse,
    PostUpdate,
)
from src.services import post as post_service

router = APIRouter(prefix="/posts", tags=["Posts"])


# ── CREATE ────────────────────────────────────────────────────────────
@router.post(
    "/",
    response_model=PostResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Tạo bài viết mới",
)
async def create_post(
    data: PostCreate,
    db: AsyncSession = Depends(get_db),
    # Day 6: chỉ author và admin được tạo bài
    current_user: User = Depends(require_role(UserRole.admin, UserRole.author)),
) -> PostResponse:
    """
    Tạo bài viết mới. Chỉ cần **title** và **content**.

    Yêu cầu: Bearer token trong header `Authorization`.
    """
    return await post_service.create_post(db, data, author_id=current_user.id)


# ── READ ALL ──────────────────────────────────────────────────────────
@router.get(
    "/",
    response_model=PaginatedPosts,
    summary="Danh sách bài viết (phân trang + lọc)",
)
async def list_posts(
    # Day 4: Query Parameters
    status_filter: Annotated[PostStatus | None, Query(alias="status", description="Lọc theo trạng thái")] = None,
    search: Annotated[str | None, Query(min_length=1, description="Tìm trong tiêu đề")] = None,
    page: Annotated[int, Query(ge=1)] = 1,
    page_size: Annotated[int, Query(ge=1, le=50)] = 10,
    db: AsyncSession = Depends(get_db),
    # Day 6: không yêu cầu auth — ai cũng xem được danh sách published
) -> PaginatedPosts:
    total, posts = await post_service.list_posts(
        db,
        status=status_filter,
        search=search,
        page=page,
        page_size=page_size,
    )
    return PaginatedPosts(total=total, page=page, page_size=page_size, posts=posts)


# ── READ ONE ──────────────────────────────────────────────────────────
@router.get(
    "/{post_id}",
    response_model=PostResponse,
    summary="Chi tiết bài viết",
)
async def get_post(
    # Day 4: Path Parameter với validation
    post_id: Annotated[int, Path(ge=1, description="ID bài viết")],
    # Day 7: Background task tăng views không block response
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db),
) -> PostResponse:
    """Xem chi tiết bài viết. Views tăng ngầm bằng background task."""
    post = await post_service.get_post(db, post_id, background_tasks)
    if not post:
        raise HTTPException(status_code=404, detail=f"Không tìm thấy bài viết id={post_id}")
    return post


# ── UPDATE ────────────────────────────────────────────────────────────
@router.patch(
    "/{post_id}",
    response_model=PostResponse,
    summary="Cập nhật bài viết (PATCH)",
)
async def update_post(
    post_id: Annotated[int, Path(ge=1)],
    data: PostUpdate,
    db: AsyncSession = Depends(get_db),
    # Day 6: phải đăng nhập
    current_user: User = Depends(get_current_active_user),
) -> PostResponse:
    """Partial update. Chỉ tác giả hoặc admin mới được sửa."""
    try:
        post = await post_service.update_post(
            db,
            post_id,
            data,
            author_id=current_user.id,
            is_admin=(current_user.role == UserRole.admin),
        )
    except PermissionError as e:
        raise HTTPException(status_code=403, detail=str(e)) from e

    if not post:
        raise HTTPException(status_code=404, detail=f"Không tìm thấy id={post_id}")
    return post


# ── DELETE ────────────────────────────────────────────────────────────
@router.delete(
    "/{post_id}",
    response_model=MessageResponse,
    summary="Xoá bài viết",
)
async def delete_post(
    post_id: Annotated[int, Path(ge=1)],
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> MessageResponse:
    """Chỉ tác giả hoặc admin mới được xoá."""
    try:
        deleted = await post_service.delete_post(
            db,
            post_id,
            author_id=current_user.id,
            is_admin=(current_user.role == UserRole.admin),
        )
    except PermissionError as e:
        raise HTTPException(status_code=403, detail=str(e)) from e

    if not deleted:
        raise HTTPException(status_code=404, detail=f"Không tìm thấy id={post_id}")
    return MessageResponse(message=f"Đã xoá bài viết id={post_id}.")