"""
src/services/auth.py — Xử lý mật khẩu và JWT token.

Day 6: passlib bcrypt + python-jose JWT.
"""
from datetime import UTC, datetime, timedelta

from jose import JWTError, jwt
from passlib.context import CryptContext

from src.config.settings import settings
from src.models.schemas import TokenPayload

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(password: str) -> str:
    """Băm mật khẩu bằng bcrypt."""
    return pwd_context.hash(password)


def verify_password(plain: str, hashed: str) -> bool:
    """Kiểm tra mật khẩu khớp với hash."""
    return pwd_context.verify(plain, hashed)


def create_access_token(user_id: int, role: str) -> str:
    """Tạo JWT access token (ngắn hạn)."""
    expire = datetime.now(UTC) + timedelta(
        minutes=settings.jwt.access_token_expire_minutes
    )
    payload = {"sub": str(user_id), "role": role, "exp": expire, "type": "access"}
    return jwt.encode(payload, settings.jwt.secret_key, algorithm=settings.jwt.algorithm)


def create_refresh_token(user_id: int) -> str:
    """Tạo JWT refresh token (dài hạn)."""
    expire = datetime.now(UTC) + timedelta(days=settings.jwt.refresh_token_expire_days)
    payload = {"sub": str(user_id), "exp": expire, "type": "refresh"}
    return jwt.encode(payload, settings.jwt.secret_key, algorithm=settings.jwt.algorithm)


def decode_token(token: str) -> TokenPayload:
    """Giải mã JWT token, raise JWTError nếu không hợp lệ."""
    payload = jwt.decode(
        token, settings.jwt.secret_key, algorithms=[settings.jwt.algorithm]
    )
    return TokenPayload(**payload)


__all__ = [
    "hash_password",
    "verify_password",
    "create_access_token",
    "create_refresh_token",
    "decode_token",
    "JWTError",
]