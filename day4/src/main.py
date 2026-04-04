"""
src/main.py — Khởi tạo FastAPI app và đăng ký routers.
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.routers.posts import router as posts_router


app = FastAPI(
    title="📝 Blog Cá Nhân API",
    description="""
API quản lý blog cá nhân — FastAPI Day 4

**Kỹ năng thực hành:**
- ✅ **Pydantic v2** — validate input & serialize output tự động
- ✅ **Path Parameters** — `/posts/{post_id}` với kiểu dữ liệu & ràng buộc
- ✅ **Query Parameters** — phân trang, lọc theo category, tìm kiếm
- ✅ **Request Headers** — `X-Author-Name` xác định tác giả
- ✅ **Cookies** — `session_token` xác thực đơn giản

**Cách test các endpoint cần xác thực:**
Dùng cookie `session_token = my_secret_token_123`
""",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(posts_router)


@app.get("/", tags=["Health"])
def root():
    return {
        "status": "ok",
        "message": "Blog API đang chạy 🚀",
        "docs": "/docs",
    }