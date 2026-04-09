# 📝 Blog API — FastAPI Day 4 → 7

API quản lý blog cá nhân, xây dựng theo từng ngày với các kỹ năng tích luỹ dần.

---

## Cấu trúc project

```
blog-api/
├── main.py                      ← Entry point
├── pyproject.toml               ← Dependencies
├── alembic.ini                  ← Cấu hình migration
├── Dockerfile                   ← Day 7
├── docker-compose.yml           ← Day 7
├── .env.example                 ← Mẫu biến môi trường
├── alembic/
│   ├── env.py                   ← Async migration config
│   └── versions/
│       └── 001_create_tables.py ← Migration đầu tiên
├── scripts/
│   └── create_admin.py          ← Tạo tài khoản admin
└── src/
    ├── config/
    │   └── settings.py          ← Pydantic Settings
    ├── db/
    │   ├── base.py              ← SQLAlchemy Base
    │   └── session.py           ← Async engine + get_db()
    ├── models/
    │   ├── orm.py               ← SQLAlchemy ORM (User, Post)
    │   └── schemas.py           ← Pydantic schemas
    ├── services/
    │   ├── auth.py              ← bcrypt + JWT
    │   ├── user.py              ← register, login
    │   └── post.py              ← CRUD + background task
    ├── deps/
    │   └── auth.py              ← get_current_user, require_role()
    └── api/
        ├── app.py               ← create_app(), middleware
        └── v1/
            ├── auth.py          ← /auth/register, /auth/login
            └── posts.py         ← /posts CRUD
```

---

## Kỹ năng theo từng ngày

### Day 4 — The Modern API
- **Pydantic v2**: `PostCreate` chỉ cần `title` + `content`, validation tự động
- **Path Params**: `GET /api/v1/posts/{post_id}` với `Path(ge=1)`
- **Query Params**: `?status=published&search=fastapi&page=1&page_size=10`
- **Headers**: `Authorization: Bearer <token>`
- **Cookies**: Server tự set `access_token` cookie sau khi login

### Day 5 — DB & Migrations
- **SQLAlchemy async**: Toàn bộ query dùng `async/await` với `asyncpg`
- **Schema design**: Bảng `users` và `posts` với relationship, index, constraint
- **Alembic**: Migration `001_create_users_and_posts.py` tạo bảng từ đầu

### Day 6 — Security & Auth
- **JWT**: `python-jose` tạo access token (30 phút) + refresh token (7 ngày)
- **bcrypt**: `passlib` băm mật khẩu an toàn
- **Middleware**: Log mọi request (method, path, status, thời gian)
- **Role-based**: `require_role(UserRole.admin, UserRole.author)` làm dependency

### Day 7 — Mini Project 1
- **Background Tasks**: Tăng `views` không block response khi `GET /posts/{id}`
- **Dockerfile**: Multi-stage build, tự chạy `alembic upgrade head` trước khi start
- **docker-compose**: `app` + `db` (PostgreSQL), `depends_on` với health check

---

## Cài đặt & Chạy

### Cách 1 — Chạy local (cần PostgreSQL)

```bash
# 1. Tạo file .env
cp .env.example .env

# 2. Cài dependencies
pip install -r requirements.txt
# hoặc
poetry install

# 3. Chạy migration
alembic upgrade head

# 4. Tạo tài khoản admin
python scripts/create_admin.py

# 5. Chạy server
uvicorn main:app --reload
```

### Cách 2 — Docker (không cần cài PostgreSQL)

```bash
# 1. Tạo file .env
cp .env.example .env

# 2. Build và chạy
docker compose up --build

# 3. Tạo admin (trong container)
docker compose exec app python scripts/create_admin.py
```

Mở: **http://localhost:8000/docs**

---

## Hướng dẫn sử dụng API

### Bước 1 — Đăng ký tài khoản

```
POST /api/v1/auth/register
```
```json
{
  "username": "nguyenvana",
  "email": "a@gmail.com",
  "password": "matkhau123",
  "full_name": "Nguyen Van A"
}
```

### Bước 2 — Đăng nhập

```
POST /api/v1/auth/login?username=nguyenvana&password=matkhau123
```

Server trả về:
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer"
}
```

> Server đồng thời **tự set cookie** `access_token` — không cần F12 Console.

### Bước 3 — Dùng token trong Swagger UI

1. Bấm nút **Authorize** (🔒) ở góc trên phải
2. Dán `access_token` vào ô **Value**
3. Bấm **Authorize** → từ nay mọi request tự kèm token

### Bước 4 — Tạo bài viết

```
POST /api/v1/posts/
```
```json
{
  "title": "Bài viết đầu tiên",
  "content": "Nội dung bài viết của tôi..."
}
```

### Các endpoint khác

| Method | Endpoint | Mô tả | Auth |
|--------|----------|-------|------|
| `GET` | `/api/v1/posts/` | Danh sách bài viết | Không |
| `GET` | `/api/v1/posts/{id}` | Chi tiết (tăng views) | Không |
| `PATCH` | `/api/v1/posts/{id}` | Sửa bài viết | Tác giả / Admin |
| `DELETE` | `/api/v1/posts/{id}` | Xoá bài viết | Tác giả / Admin |
| `POST` | `/api/v1/auth/logout` | Đăng xuất | Không |

---

## HTTP Status Codes

| Code | Ý nghĩa |
|------|---------|
| `200 OK` | Thành công |
| `201 Created` | Tạo mới thành công |
| `400 Bad Request` | Dữ liệu không hợp lệ |
| `401 Unauthorized` | Chưa đăng nhập / token hết hạn |
| `403 Forbidden` | Không đủ quyền |
| `404 Not Found` | Không tìm thấy |
| `422 Unprocessable Entity` | Lỗi validation Pydantic |