# 🛒 Shop Service — Django Day 8 → 13

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
├── tests/                      ← Unit tests (Day 13)
│   ├── conftest.py             ← Fixtures dùng chung
│   ├── test_inventory.py       ← Tests cho Category, Product, API
│   ├── test_cart.py            ← Tests cho Cart, CartItem, API
│   ├── test_orders.py          ← Tests cho Checkout, Signals (mock Celery)
│   └── test_users.py           ← Tests cho Auth, JWT, Register/Login
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

### Day 13 — Testing & Quality
- **pytest-django**: fixtures, `db` marker, `APIClient`
- **Mocking**: `@patch` mock Celery task và Django Signal
- **Coverage**: đạt ≥ 80% cho toàn bộ module
- **Edge cases**: hết hàng, giỏ trống, sai quyền, token hết hạn

---

## Cài đặt & Chạy

### Cách 1 — Docker (khuyên dùng)

```bash
cp .env.example .env
docker compose up -d --build   
docker compose exec app python scripts/seed_data.py
```

### Cách 2 — Local với uv

```bash
# Cài uv nếu chưa có
pip install uv

# Cài toàn bộ dependencies
uv sync

# Cấu hình
cp .env.example .env   # chỉnh DATABASE_URL và REDIS_URL

# Migrate và seed
uv run python manage.py migrate
uv run python scripts/seed_data.py

# Chạy server
uv run python manage.py runserver

# Chạy Celery worker (mở terminal khác)
uv run celery -A config worker --loglevel=info
```

---

## Chạy Tests (Day 13)

> **💡 Lưu ý:** Toàn bộ hệ thống kiểm thử (`pytest`, `pytest-django`, `pytest-cov`, `factory-boy`) đã được đóng gói sẵn vào trong container `app` thông qua `Dockerfile`. Bạn không cần phải cài đặt thủ công thêm bất kỳ thư viện nào trên máy chủ (host).

Để chạy test, chúng ta sẽ gửi lệnh thực thi trực tiếp vào bên trong container `app`.

### 1. Chạy toàn bộ bài test & Báo cáo độ bao phủ (Coverage)
docker compose exec app pytest tests/ -v --cov=apps --cov-report=term-missing

### 2. Chạy test theo từng Module chức năng
# Test phân hệ Kho hàng (Category, Product)
docker compose exec app pytest tests/test_inventory.py -v

# Test phân hệ Giỏ hàng (Cart, CartItem)
docker compose exec app pytest tests/test_cart.py -v

# Test phân hệ Đơn hàng (Order, Checkout, Celery Tasks, Signals)
docker compose exec app pytest tests/test_orders.py -v

# Test phân hệ Người dùng (Auth, Register, JWT)
docker compose exec app pytest tests/test_users.py -v

### 3. Chạy test siêu tốc cho 1 Class hoặc 1 Function
# Chỉ chạy toàn bộ các test trong Class TestCheckoutAPI
docker compose exec app pytest tests/test_orders.py::TestCheckoutAPI -v

# Chỉ chạy chính xác 1 hàm test_add_product_to_cart
docker compose exec app pytest tests/test_cart.py::TestCartAPI::test_add_product_to_cart -v

### Kỹ thuật test quan trọng
**Fixtures** — tạo dữ liệu test dùng lại (`conftest.py`):
```python
@pytest.fixture
def product(db, category):
    return Product.objects.create(name="iPhone", price=28_990_000, stock=50)
```

**Mock Celery task** — không gửi email thật khi test (`test_orders.py`):
```python
@patch("apps.orders.tasks.send_order_confirmation_email.delay")
def test_checkout_calls_celery(self, mock_email, auth_client, ...):
    # thực hiện checkout ...
    mock_email.assert_called_once()   # ← kiểm tra task được gọi
```

**Mock Signal** — kiểm tra signal hoàn kho khi huỷ đơn:
```python
@patch("apps.orders.tasks.restore_stock_on_cancel.delay")
def test_signal_on_cancel(self, mock_restore, pending_order):
    pending_order.status = Order.Status.CANCELLED
    pending_order.save()
    mock_restore.assert_called_once_with(pending_order.pk)
```

---

## Hướng dẫn test API bằng Postman

### Bước 1 — Import collection

1. Mở Postman → bấm **Import**
2. Kéo thả file `shop-service.postman_collection.json` vào
3. Bấm **Import** → xuất hiện collection **Shop Service API**

### Bước 2 — Tạo dữ liệu mẫu

Trước khi test, chạy seed data để có sản phẩm và tài khoản sẵn:

```bash
# Docker
docker compose exec app python scripts/seed_data.py

# Local
uv run python scripts/seed_data.py
```

Tài khoản được tạo sẵn:

| Tài khoản | Email | Password | Quyền |
|-----------|-------|----------|-------|
| Admin | admin@shop.com | admin123 | Tất cả |
| Khách hàng | khach@shop.com | khach123 | Mua hàng |

### Bước 3 — Đăng nhập lấy token

Trong Postman, mở folder **Auth** → chạy request **Login**:
- Token tự động lưu vào biến `{{access_token}}`
- Tất cả request sau tự động kèm token — **không cần copy dán thủ công**

> Dùng **Login (Admin)** để test tạo sản phẩm, đổi trạng thái đơn hàng.
> Dùng **Login (Khách hàng)** để test mua hàng, đặt đơn.

### Bước 4 — Test theo luồng mua hàng

Chạy các request theo thứ tự sau:

```
1. Auth / Login                          → lấy token tự động
   ↓
2. Inventory / Danh sách sản phẩm        → xem toàn bộ sản phẩm
   ↓
3. Inventory / Tìm kiếm sản phẩm         → tìm theo tên
   ↓
4. Inventory / Lọc theo danh mục + giá  → lọc min_price, max_price
   ↓
5. Cart / Thêm vào giỏ                   → nhập product_id + quantity
   ↓
6. Cart / Xem giỏ hàng                   → kiểm tra items + tổng tiền
   ↓
7. Orders / Đặt hàng (Checkout)          → nhập shipping_address
   ↓
8. Orders / Danh sách đơn hàng           → xem đơn vừa tạo
   ↓
9. Orders / Chi tiết đơn hàng            → dùng {{order_id}} tự động
```

### Bước 5 — Test phân quyền

Đăng nhập bằng tài khoản **khách hàng** rồi thử:

```
POST /inventory/products/   → 403 Forbidden  (không tạo được sản phẩm)
POST /orders/{id}/update_status/ → 403 Forbidden  (không đổi được trạng thái)
```

Đăng nhập bằng **admin** rồi thử:

```
POST /inventory/products/         → 201 Created  ✅
POST /orders/{id}/update_status/  → 200 OK  ✅
```

### Các biến tự động trong collection

| Biến | Được lưu khi | Dùng ở đâu |
|------|-------------|------------|
| `{{access_token}}` | Chạy Login | Tất cả request cần auth |
| `{{refresh_token}}` | Chạy Login | Request Refresh Token |
| `{{product_slug}}` | Xem chi tiết sản phẩm | Update/Delete sản phẩm |
| `{{order_id}}` | Đặt hàng Checkout | Chi tiết, huỷ, đổi trạng thái |

---

## Hướng dẫn test API bằng Swagger UI

Mở: **http://127.0.0.1:8000/api/docs/**

### Đăng nhập trên Swagger

1. Tìm `POST /api/v1/auth/token/` → bấm **Try it out**
2. Nhập email và password → bấm **Execute**
3. Copy giá trị `access` trong response
4. Bấm nút **Authorize 🔒** góc trên phải
5. Nhập `Bearer <token vừa copy>` → bấm **Authorize**

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
| `422 Unprocessable Entity` | Dữ liệu không đúng định dạng |