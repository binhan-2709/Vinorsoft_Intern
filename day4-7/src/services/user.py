"""
src/services/user.py — Đăng ký và xác thực người dùng.

Day 6: Kết hợp với auth service để tạo JWT.
"""
import structlog
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.models.orm import User
from src.models.schemas import TokenResponse, UserRegister, UserResponse
from src.services.auth import (
    create_access_token,
    create_refresh_token,
    hash_password,
    verify_password,
)

logger = structlog.get_logger()


async def register_user(db: AsyncSession, data: UserRegister) -> UserResponse:
    """Đăng ký tài khoản mới."""
    # Kiểm tra username/email đã tồn tại chưa
    existing = await db.execute(
        select(User).where(
            (User.username == data.username) | (User.email == data.email)
        )
    )
    if existing.scalar_one_or_none():
        raise ValueError("Username hoặc email đã được sử dụng.")

    user = User(
        username=data.username,
        email=data.email,
        hashed_password=hash_password(data.password),
        full_name=data.full_name,
    )
    db.add(user)
    
    # 🌟 SỬA Ở ĐÂY: Dùng commit để lưu thật vào Database thay vì chỉ lưu nháp (flush)
    await db.commit()
    await db.refresh(user)
    
    logger.info("user_registered", user_id=user.id, username=user.username)
    return UserResponse.model_validate(user)


async def login_user(db: AsyncSession, username: str, password: str) -> TokenResponse:
    """Đăng nhập, trả về JWT tokens."""
    result = await db.execute(select(User).where(User.username == username))
    user = result.scalar_one_or_none()

    if not user or not verify_password(password, user.hashed_password):
        raise ValueError("Sai username hoặc mật khẩu.")
    if not user.is_active:
        raise ValueError("Tài khoản đã bị khoá.")

    logger.info("user_logged_in", user_id=user.id)
    return TokenResponse(
        access_token=create_access_token(user.id, user.role.value),
        refresh_token=create_refresh_token(user.id),
    )


async def get_user_by_id(db: AsyncSession, user_id: int) -> User | None:
    result = await db.execute(select(User).where(User.id == user_id))
    return result.scalar_one_or_none()