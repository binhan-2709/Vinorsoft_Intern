# 🛒 Shop Service — Django Day 8 → 12

E-commerce backend xây dựng với Django + DRF + Celery theo từng ngày.

---

## Cấu trúc project

```
shop-service/
├── manage.py
├── pyproject.toml
├── Dockerfile
├── docker-compose.yml          ← app + db + redis + celery
├── .env.example
├── config/
│   ├── __init__.py             ← load celery khi start
│   ├── celery.py               ← Celery app (Day 11)
│   ├── urls.py                 ← URL routing chính
│   ├── wsgi.py
│   └── settings/
│       ├── base.py             ← Cấu hình chung
│       ├── local.py            ← Dev
│       └── production.py       ← Production
├── apps/
│   ├── users/                  ← Custom User + JWT Auth
│   │   ├── models.py           ← AbstractUser + role
│   │   ├── serializers.py      ← RegisterSerializer
│   │   ├── views.py            ← Register, Me
│   │   ├── urls.py
│   │   └── admin.py
│   ├── inventory/              ← Kho hàng (Day 8, 9)
│   │   ├── models.py           ← Category, Product + custom Manager
│   │   ├── serializers.py      ← Nested serializer
│   │   ├── views.py            ← ModelViewSet + custom action
│   │   ├── urls.py             ← DefaultRouter
│   │   └── admin.py            ← Admin với inline, action, badge
│   ├── cart/                   ← Giỏ hàng (Day 10)
│   │   ├── models.py           ← Cart (OneToOne), CartItem (FK)
│   │   ├── serializers.py
│   │   ├── views.py            ← get_or_create, update_or_create
│   │   └── urls.py
│   └── orders/                 ← Đơn hàng (Day 11, 12)
│       ├── models.py           ← Order, OrderItem (snapshot giá)
│       ├── serializers.py
│       ├── views.py            ← checkout() với transaction.atomic()
│       ├── signals.py          ← post_save → Celery task
│       ├── tasks.py            ← send_email, restore_stock
│       ├── urls.py
│       └── admin.py
└── scripts/
    └── seed_data.py            ← Tạo dữ liệu mẫu
```

---

## Kỹ năng theo từng ngày

### Day 8 — Django Batteries-included
- **Custom User**: extend `AbstractUser`, thêm `role`, `phone`
- **Django Admin**: `list_display`, `list_editable`, `inline`, `action`, badge màu
- **ORM nâng cao**: custom `Manager`, `QuerySet` (`in_stock()`, `by_category()`)
- **Meta**: `ordering`, `indexes`, `db_table`, `verbose_name`

### Day 9 — Django REST Framework
- **ModelSerializer**: tự sinh fields từ model, `SerializerMethodField`, nested
- **ModelViewSet**: 5 endpoint CRUD chỉ với ~10 dòng code
- **DefaultRouter**: tự tạo URL từ ViewSet
- **Filtering**: `django-filter` lọc theo giá, tồn kho
- **Auth**: `simplejwt` — `TokenObtainPairView`, `TokenRefreshView`
- **Docs**: `drf-spectacular` → Swagger tự động tại `/api/docs/`

### Day 10 — Relationships & Ops
- **One-to-One**: `User` ↔ `Cart` (mỗi user 1 giỏ)
- **One-to-Many**: `Cart` → `CartItem`, `Order` → `OrderItem`
- **ForeignKey**: `Product` trong `CartItem`, `OrderItem`
- **select_related**: tránh N+1 khi lấy `category` của `Product`
- **prefetch_related**: tránh N+1 khi lấy `items` của `Cart`
- **unique_together**: 1 sản phẩm chỉ 1 dòng trong giỏ

### Day 11 — Task Queue & Signal
- **Django Signals**: `post_save` → tự gọi Celery khi Order tạo mới
- **pre_save**: phát hiện status thay đổi, hoàn kho khi huỷ
- **Celery task**: `send_order_confirmation_email.delay(order_id)` — không block request
- **retry**: task tự retry tối đa 3 lần khi lỗi
- **Redis**: làm message broker cho Celery

### Day 12 — Mini Project 2
- **checkout()**: `transaction.atomic()` đảm bảo toàn vẹn — trừ kho + tạo đơn + xoá giỏ
- **Snapshot giá**: `unit_price` lưu giá lúc đặt, không bị thay đổi sau
- **bulk_create**: tạo nhiều `OrderItem` trong 1 query
- **Status workflow**: pending → confirmed → shipping → delivered / cancelled
- **Docker**: 4 service — app, db, redis, celery

---

## Cài đặt & Chạy

### Cách 1 — Docker (khuyên dùng)

```bash
cp .env.example .env
docker compose up --build
docker compose exec app python scripts/seed_data.py
```

### Cách 2 — Local

```bash
# Cài dependencies
pip install django djangorestframework djangorestframework-simplejwt \
    django-filter drf-spectacular psycopg[binary] django-environ \
    celery redis django-celery-results pillow structlog

# Cấu hình
cp .env.example .env   # chỉnh DATABASE_URL và REDIS_URL

# Migrate và seed
python manage.py migrate
python scripts/seed_data.py

# Chạy server
python manage.py runserver

# Chạy Celery worker (terminal khác)
celery -A config worker --loglevel=info
```

---

## Hướng dẫn test API

Mở: **http://127.0.0.1:8000/api/docs/**

### 1. Đăng nhập lấy token
```
POST /api/v1/auth/token/
{ "email": "khach@shop.com", "password": "khach123" }
```
Copy `access` token → bấm **Authorize** 🔒 → dán vào.

### 2. Xem sản phẩm
```
GET /api/v1/inventory/products/
GET /api/v1/inventory/products/?min_price=100000&in_stock=true
GET /api/v1/inventory/products/in_stock/
```

### 3. Thêm vào giỏ
```
POST /api/v1/cart/add/
{ "product_id": 1, "quantity": 2 }
```

### 4. Đặt hàng
```
POST /api/v1/orders/checkout/
{ "shipping_address": "123 Đường ABC, Hà Nội", "note": "Giao buổi sáng" }
```
→ Signal tự kích hoạt → Celery gửi email xác nhận

### 5. Xem đơn hàng
```
GET /api/v1/orders/
GET /api/v1/orders/{id}/
POST /api/v1/orders/{id}/cancel/
```

### 6. Django Admin (quản lý kho)
```
http://127.0.0.1:8000/admin
admin@shop.com / admin123
```

---

## HTTP Status Codes

| Code | Ý nghĩa |
|------|---------|
| `200 OK` | Thành công |
| `201 Created` | Tạo mới thành công |
| `400 Bad Request` | Lỗi dữ liệu (giỏ trống, hết hàng...) |
| `401 Unauthorized` | Chưa đăng nhập |
| `403 Forbidden` | Không đủ quyền |
| `404 Not Found` | Không tìm thấy |
