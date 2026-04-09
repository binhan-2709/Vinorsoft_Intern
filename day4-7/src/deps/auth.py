"""
src/deps/auth.py — FastAPI dependencies cho xác thực và phân quyền.

Day 6: JWT Bearer token + Role-based access control.
"""
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jose import JWTError
from sqlalchemy.ext.asyncio import AsyncSession

from src.db.session import get_db
from src.models.orm import User, UserRole
from src.services.auth import decode_token
from src.services.user import get_user_by_id

bearer_scheme = HTTPBearer(auto_error=False)

_401 = HTTPException(
    status_code=status.HTTP_401_UNAUTHORIZED,
    detail="Token không hợp lệ hoặc đã hết hạn.",
    headers={"WWW-Authenticate": "Bearer"},
)
_403 = HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Không có quyền truy cập.")


async def get_current_user(
    credentials: HTTPAuthorizationCredentials | None = Depends(bearer_scheme),
    db: AsyncSession = Depends(get_db),
) -> User:
    """Lấy user hiện tại từ JWT Bearer token."""
    if not credentials:
        raise _401
    try:
        payload = decode_token(credentials.credentials)
    except JWTError:
        raise _401

    user = await get_user_by_id(db, int(payload.sub))
    if not user or not user.is_active:
        raise _401
    return user


async def get_current_active_user(
    current_user: User = Depends(get_current_user),
) -> User:
    """Chỉ cho phép user đang active."""
    if not current_user.is_active:
        raise HTTPException(status_code=400, detail="Tài khoản không hoạt động.")
    return current_user


def require_role(*roles: UserRole):
    """
    Dependency factory: chỉ cho phép user có role nhất định.

    Dùng: Depends(require_role(UserRole.admin, UserRole.author))
    """

    async def _check(current_user: User = Depends(get_current_active_user)) -> User:
        if current_user.role not in roles:
            raise _403
        return current_user

    return _check