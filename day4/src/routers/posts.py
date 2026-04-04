"""
routers/posts.py — CRUD endpoints cho bài viết.

Minh hoạ:
  ✅ Path Parameters   /posts/{post_id}
  ✅ Query Parameters  ?page= &category= &search= &published=
  ✅ Request Headers   X-Author-Name
  ✅ Cookies           session_token
"""
from fastapi import APIRouter, HTTPException, Path, Query, Header, Cookie, status
from typing import Annotated

from src.models import (
    PostCreate, PostUpdate,
    PostResponse, PaginatedPosts, MessageResponse,
    Category,
)
from src.database import (
    db_create_post, db_get_post,
    db_list_posts, db_update_post, db_delete_post,
)

router = APIRouter(prefix="/posts", tags=["Posts"])

# ── Token cứng cho mục đích học tập ──────────────────────────────────
VALID_TOKEN = "my_secret_token_123"


def require_auth(session_token: str | None) -> None:
    """Raise 401 nếu cookie session_token không hợp lệ."""
    if session_token != VALID_TOKEN:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Chưa đăng nhập. Gửi cookie: session_token=my_secret_token_123",
        )


# ── CREATE ────────────────────────────────────────────────────────────
@router.post(
    "/",
    response_model=PostResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Tạo bài viết mới",
)
def create_post(
    data: PostCreate,
    x_author_name: Annotated[str, Header(description="Tên tác giả")] = "Anonymous",
    session_token: Annotated[str | None, Cookie()] = None,
):
    """
    **Headers cần thiết:**
    - `X-Author-Name`: tên tác giả (mặc định: Anonymous)

    **Cookie cần thiết:**
    - `session_token = my_secret_token_123`
    """
    require_auth(session_token)
    return db_create_post(data, author=x_author_name)


# ── READ ALL ──────────────────────────────────────────────────────────
@router.get(
    "/",
    response_model=PaginatedPosts,
    summary="Danh sách bài viết (phân trang + lọc)",
)
def list_posts(
    published:  Annotated[bool, Query(description="Chỉ lấy bài đã published")] = False,
    category:   Annotated[Category | None, Query(description="Lọc theo category")] = None,
    search:     Annotated[str | None, Query(min_length=1, description="Tìm trong title/content")] = None,
    page:       Annotated[int, Query(ge=1, description="Trang hiện tại")] = 1,
    page_size:  Annotated[int, Query(ge=1, le=50, description="Số bài mỗi trang")] = 10,
):
    """
    Ví dụ: `GET /posts/?published=true&category=tech&search=fastapi&page=1`
    """
    total, posts = db_list_posts(
        published_only=published,
        category=category,
        search=search,
        page=page,
        page_size=page_size,
    )
    return PaginatedPosts(total=total, page=page, page_size=page_size, posts=posts)


# ── READ ONE ──────────────────────────────────────────────────────────
@router.get(
    "/{post_id}",
    response_model=PostResponse,
    summary="Chi tiết một bài viết",
)
def get_post(
    post_id: Annotated[int, Path(ge=1, description="ID bài viết (số nguyên ≥ 1)")],
):
    """Mỗi lần gọi tăng `views` lên 1."""
    post = db_get_post(post_id)
    if not post:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Không tìm thấy bài viết id={post_id}",
        )
    return post


# ── UPDATE ────────────────────────────────────────────────────────────
@router.patch(
    "/{post_id}",
    response_model=PostResponse,
    summary="Cập nhật một phần bài viết (PATCH)",
)
def update_post(
    post_id: Annotated[int, Path(ge=1)],
    data: PostUpdate,
    session_token: Annotated[str | None, Cookie()] = None,
):
    """Chỉ gửi field muốn thay đổi — các field còn lại giữ nguyên."""
    require_auth(session_token)
    post = db_update_post(post_id, data)
    if not post:
        raise HTTPException(status_code=404, detail=f"Không tìm thấy id={post_id}")
    return post


# ── DELETE ────────────────────────────────────────────────────────────
@router.delete(
    "/{post_id}",
    response_model=MessageResponse,
    summary="Xoá bài viết",
)
def delete_post(
    post_id: Annotated[int, Path(ge=1)],
    session_token: Annotated[str | None, Cookie()] = None,
):
    require_auth(session_token)
    if not db_delete_post(post_id):
        raise HTTPException(status_code=404, detail=f"Không tìm thấy id={post_id}")
    return MessageResponse(message=f"Đã xoá bài viết id={post_id} thành công.")