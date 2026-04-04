# 📝 Blog Cá Nhân API — Day 4

API quản lý blog cá nhân xây dựng bằng **FastAPI**, thực hành các kỹ năng:
Pydantic · Path Parameters · Query Parameters · Headers · Cookies

---

## Cài đặt & Chạy

```bash
# 1. Cài dependencies
pip install -r requirements.txt

# 2. Chạy server
uvicorn main:app --reload
```

Mở trình duyệt tại: **http://127.0.0.1:8000/docs**

---

## Hướng dẫn sử dụng Swagger UI

### Bước 1 — Đăng nhập (bắt buộc trước khi tạo/sửa/xoá)

Các endpoint **POST / PATCH / DELETE** yêu cầu xác thực bằng cookie.

Để đăng nhập, nhấn `F12` mở DevTools → chọn tab **Console** → dán dòng sau rồi nhấn **Enter**:

```javascript
document.cookie = "session_token=my_secret_token_123"
```

Sau đó **refresh lại trang** `http://127.0.0.1:8000/docs`.

> **Lưu ý:** Đây là cách xác thực đơn giản cho mục đích học tập.  
> Trong thực tế, cookie sẽ được server tự tạo và gửi về sau khi đăng nhập bằng username/password.

---

### Bước 2 — Tạo bài viết mới `POST /posts/`

1. Bấm vào **POST /posts/**
2. Bấm **Try it out**
3. Nhập body JSON:

```json
{
  "title": "Bài viết đầu tiên của tôi",
  "content": "Đây là nội dung bài viết, phải dài hơn 10 ký tự."
}
```

4. Bấm **Execute**
5. Kết quả trả về **201 Created** kèm thông tin bài viết — lưu lại `id` để dùng ở các bước sau

---

### Bước 3 — Xem danh sách bài viết `GET /posts/`

Bấm **Try it out** → **Execute** để lấy toàn bộ danh sách.

Có thể lọc bằng các query param:

| Param | Mô tả | Ví dụ |
|-------|-------|-------|
| `published` | Chỉ lấy bài đã publish | `true` |
| `category` | Lọc theo chủ đề | `tech` |
| `search` | Tìm kiếm trong tiêu đề/nội dung | `fastapi` |
| `page` | Số trang | `1` |
| `page_size` | Số bài mỗi trang | `5` |

---

### Bước 4 — Xem chi tiết một bài `GET /posts/{post_id}`

1. Bấm **Try it out**
2. Nhập `post_id` (số nguyên, ví dụ: `1`)
3. Bấm **Execute**

> Mỗi lần gọi endpoint này, trường `views` tăng lên 1.

---

### Bước 5 — Cập nhật bài viết `PATCH /posts/{post_id}`

Chỉ cần gửi field muốn thay đổi, các field khác giữ nguyên:

```json
{
  "title": "Tiêu đề mới"
}
```

hoặc:

```json
{
  "published": true
}
```

---

### Bước 6 — Xoá bài viết `DELETE /posts/{post_id}`

1. Bấm **Try it out**
2. Nhập `post_id` cần xoá
3. Bấm **Execute**
4. Kết quả trả về message xác nhận

---

## Cấu trúc project

```
day4/
├── main.py              ← Entry point
├── pyproject.toml       ← Cấu hình dependencies
└── src/
    ├── __init__.py
    ├── main.py          ← Khởi tạo FastAPI app
    ├── models.py        ← Pydantic schemas
    ├── database.py      ← In-memory database
    └── routers/
        ├── __init__.py
        └── posts.py     ← CRUD endpoints
```

---

## Các kỹ năng thực hành

| Kỹ năng | Ví dụ trong code |
|---------|-----------------|
| **Pydantic** | `PostCreate`, `PostUpdate`, `PostResponse` — validate & serialize tự động |
| **Path Params** | `GET /posts/{post_id}` với `Path(ge=1)` |
| **Query Params** | `?published=true&category=tech&page=1` |
| **Headers** | `X-Author-Name` — xác định tên tác giả |
| **Cookies** | `session_token` — xác thực đơn giản |

---

## HTTP Status Codes

| Code | Ý nghĩa |
|------|---------|
| `200 OK` | Thành công (GET, PATCH, DELETE) |
| `201 Created` | Tạo mới thành công (POST) |
| `401 Unauthorized` | Chưa đăng nhập (thiếu cookie) |
| `404 Not Found` | Không tìm thấy bài viết |
| `422 Unprocessable Entity` | Dữ liệu gửi lên không hợp lệ |