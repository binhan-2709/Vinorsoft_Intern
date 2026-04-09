"""
src/db/session.py — Async SQLAlchemy engine và session factory.

Day 5: Kết nối PostgreSQL bằng asyncpg qua SQLAlchemy async.
"""
from collections.abc import AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from src.config.settings import settings

# ── Engine (Day 5) ────────────────────────────────────────────────────
engine = create_async_engine(
    settings.database.url,
    echo=settings.debug,          # In SQL ra console khi debug=True
    pool_size=10,
    max_overflow=20,
    pool_pre_ping=True,           # Kiểm tra connection trước khi dùng
)

AsyncSessionLocal = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,        # Không expire object sau commit
)


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """
    Dependency injection: cung cấp DB session cho từng request.

    Tự động commit nếu không có lỗi, rollback nếu có exception.
    """
    async with AsyncSessionLocal() as session:
        try:
            yield session
            if session.in_transaction():
                await session.commit()
        except Exception:
            if session.in_transaction():
                await session.rollback()
            raise