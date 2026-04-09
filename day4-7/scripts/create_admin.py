"""
scripts/create_admin.py — Tạo tài khoản admin để test.

Chạy: python scripts/create_admin.py
"""
import asyncio
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.db.session import AsyncSessionLocal
from src.models.orm import User, UserRole
from src.services.auth import hash_password


async def main() -> None:
    async with AsyncSessionLocal() as db:
        admin = User(
            username="admin",
            email="admin@blog.com",
            hashed_password=hash_password("admin123"),
            full_name="Administrator",
            role=UserRole.admin,
        )
        db.add(admin)
        await db.commit()
        print("✅ Tạo admin thành công!")
        print("   Username: admin")
        print("   Password: admin123")


if __name__ == "__main__":
    asyncio.run(main())