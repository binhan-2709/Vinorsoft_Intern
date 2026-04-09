"""
src/api/v1/auth.py — Endpoints đăng ký và đăng nhập.

Day 6: Trả về JWT tokens, server tự set cookie.
"""
from fastapi import APIRouter, Depends, HTTPException, Response, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.db.session import get_db
from src.models.schemas import MessageResponse, TokenResponse, UserRegister, UserResponse
from src.services.user import login_user, register_user

router = APIRouter(prefix="/auth", tags=["Auth"])


@router.post(
    "/register",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Đăng ký tài khoản mới",
)
async def register(data: UserRegister, db: AsyncSession = Depends(get_db)) -> UserResponse:
    """Tạo tài khoản mới với username/email/password."""
    try:
        return await register_user(db, data)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e)) from e


@router.post(
    "/login",
    response_model=TokenResponse,
    summary="Đăng nhập — nhận JWT token",
)
async def login(
    username: str,
    password: str,
    response: Response,
    db: AsyncSession = Depends(get_db),
) -> TokenResponse:
    """
    Đăng nhập và nhận JWT tokens.

    Server tự set **cookie** `access_token` đồng thời trả về token trong body.
    Từ đó các request tiếp theo tự động được xác thực.
    """
    try:
        tokens = await login_user(db, username, password)
    except ValueError as e:
        raise HTTPException(status_code=401, detail=str(e)) from e

    # Server tự set cookie — người dùng không cần F12 nữa (Day 6)
    response.set_cookie(
        key="access_token",
        value=f"Bearer {tokens.access_token}",
        httponly=True,      # Không cho JS đọc (bảo mật hơn)
        samesite="lax",
        max_age=1800,       # 30 phút
    )
    return tokens


@router.post("/logout", response_model=MessageResponse, summary="Đăng xuất")
async def logout(response: Response) -> MessageResponse:
    """Xoá cookie access_token."""
    response.delete_cookie("access_token")
    return MessageResponse(message="Đăng xuất thành công.")