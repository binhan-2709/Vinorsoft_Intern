import structlog
from fastapi import BackgroundTasks
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from src.models.orm import Post, PostStatus
from src.models.schemas import PostCreate, PostResponse, PostUpdate

logger = structlog.get_logger()


# ── Background task (Day 7) ───────────────────────────────────────────
async def _log_view(post_id: int) -> None:
    """Background task: ghi log lượt xem (không block request)."""
    logger.info("post_viewed", post_id=post_id)


# ── CRUD ──────────────────────────────────────────────────────────────

async def create_post(db: AsyncSession, data: PostCreate, author_id: int) -> PostResponse:
    """Tạo bài viết mới."""
    post = Post(title=data.title, content=data.content, author_id=author_id)
    db.add(post)
    await db.commit() 
     
    # lệnh refresh này sẽ tự động lấy luôn cả thông tin author cho bạn.
    await db.refresh(post) 
    
    logger.info("post_created", post_id=post.id, author_id=author_id)
    return _to_response(post)

async def get_post(
    db: AsyncSession,
    post_id: int,
    background_tasks: BackgroundTasks | None = None,
) -> PostResponse | None:
    """Lấy chi tiết bài viết, tăng views bằng background task."""
    result = await db.execute(
        select(Post).where(Post.id == post_id) # Không cần .options nữa vì đã có lazy="selectin" ở ORM
    )
    post = result.scalar_one_or_none()
    if not post:
        return None

    post.views += 1

    if background_tasks:
        background_tasks.add_task(_log_view, post_id)

    return _to_response(post)


async def list_posts(
    db: AsyncSession,
    *,
    author_id: int | None = None,
    status: PostStatus | None = None,
    search: str | None = None,
    page: int = 1,
    page_size: int = 10,
) -> tuple[int, list[PostResponse]]:
    """Lấy danh sách bài viết có lọc và phân trang."""
    # 🌟 Thêm selectinload ngay từ câu query gốc
    query = select(Post).options(selectinload(Post.author))

    if author_id:
        query = query.where(Post.author_id == author_id)
    if status:
        query = query.where(Post.status == status)
    if search:
        query = query.where(Post.title.ilike(f"%{search}%"))

    # Count total
    count_result = await db.execute(select(func.count()).select_from(query.subquery()))
    total = count_result.scalar_one()

    # Paginate
    query = query.offset((page - 1) * page_size).limit(page_size).order_by(Post.created_at.desc())
    result = await db.execute(query)
    posts = result.scalars().all()

    return total, [_to_response(p) for p in posts]


async def update_post(
    db: AsyncSession, post_id: int, data: PostUpdate, author_id: int, is_admin: bool = False
) -> PostResponse | None:
    """Cập nhật bài viết — chỉ tác giả hoặc admin."""
    # 🌟 Thêm selectinload
    result = await db.execute(
        select(Post).options(selectinload(Post.author)).where(Post.id == post_id)
    )
    post = result.scalar_one_or_none()

    if not post:
        return None
    if not is_admin and post.author_id != author_id:
        raise PermissionError("Bạn không có quyền sửa bài viết này.")

    if data.title is not None:
        post.title = data.title
    if data.content is not None:
        post.content = data.content
    if data.status is not None:
        post.status = data.status

    await db.commit()  # 🌟 Đổi flush thành commit
    await db.refresh(post)
    return _to_response(post)


async def delete_post(
    db: AsyncSession, post_id: int, author_id: int, is_admin: bool = False
) -> bool:
    """Xoá bài viết — chỉ tác giả hoặc admin."""
    result = await db.execute(select(Post).where(Post.id == post_id))
    post = result.scalar_one_or_none()

    if not post:
        return False
    if not is_admin and post.author_id != author_id:
        raise PermissionError("Bạn không có quyền xoá bài viết này.")

    await db.delete(post)
    await db.commit()  # 🌟 Cần commit để xoá thật khỏi Database
    return True


def _to_response(post: Post) -> PostResponse:
    return PostResponse(
        id=post.id,
        title=post.title,
        content=post.content,
        status=post.status,
        views=post.views,
        author_id=post.author_id,
        author_name=post.author.username if post.author else None,
        created_at=post.created_at,
        updated_at=post.updated_at,
    )