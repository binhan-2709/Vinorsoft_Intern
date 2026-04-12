"""
tests/conftest.py — Fixtures dùng chung cho toàn bộ test suite.

Day 13: pytest fixtures, factory pattern, test database isolation.
"""
import pytest
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient

from apps.inventory.models import Category, Product
from apps.cart.models import Cart, CartItem
from apps.orders.models import Order, OrderItem

User = get_user_model()


# ── Client fixtures ───────────────────────────────────────────────────

@pytest.fixture
def api_client():
    """APIClient không xác thực."""
    return APIClient()


@pytest.fixture
def auth_client(customer_user):
    """APIClient đã đăng nhập bằng tài khoản khách hàng."""
    client = APIClient()
    client.force_authenticate(user=customer_user)
    return client


@pytest.fixture
def admin_client(admin_user):
    """APIClient đã đăng nhập bằng tài khoản admin."""
    client = APIClient()
    client.force_authenticate(user=admin_user)
    return client


# ── User fixtures ─────────────────────────────────────────────────────

@pytest.fixture
def admin_user(db):
    """Tạo admin user."""
    return User.objects.create_superuser(
        username="admin",
        email="admin@test.com",
        password="admin123",
        role=User.Role.ADMIN,
    )


@pytest.fixture
def customer_user(db):
    """Tạo khách hàng."""
    return User.objects.create_user(
        username="khachhang",
        email="khach@test.com",
        password="khach123",
        role=User.Role.CUSTOMER,
    )


@pytest.fixture
def another_user(db):
    """Tạo user thứ hai để test phân quyền."""
    return User.objects.create_user(
        username="user2",
        email="user2@test.com",
        password="user2pass",
    )


# ── Inventory fixtures ────────────────────────────────────────────────

@pytest.fixture
def category(db):
    """Tạo danh mục."""
    return Category.objects.create(name="Điện tử", description="Thiết bị điện tử")


@pytest.fixture
def product(db, category):
    """Tạo sản phẩm còn hàng."""
    return Product.objects.create(
        name="iPhone 15 Pro",
        price=28_990_000,
        stock=50,
        category=category,
        is_active=True,
    )


@pytest.fixture
def out_of_stock_product(db, category):
    """Tạo sản phẩm hết hàng."""
    return Product.objects.create(
        name="Hàng hết",
        price=100_000,
        stock=0,
        category=category,
        is_active=True,
    )


@pytest.fixture
def inactive_product(db, category):
    """Tạo sản phẩm đã ẩn."""
    return Product.objects.create(
        name="Sản phẩm ẩn",
        price=500_000,
        stock=10,
        category=category,
        is_active=False,
    )


# ── Cart fixtures ─────────────────────────────────────────────────────

@pytest.fixture
def cart_with_item(db, customer_user, product):
    """Tạo giỏ hàng có sẵn 1 sản phẩm."""
    cart = Cart.objects.create(user=customer_user)
    CartItem.objects.create(cart=cart, product=product, quantity=2)
    return cart


# ── Order fixtures ────────────────────────────────────────────────────

@pytest.fixture
def pending_order(db, customer_user, product):
    """Tạo đơn hàng đang chờ xử lý."""
    order = Order.objects.create(
        user=customer_user,
        shipping_address="123 Đường Test, Hà Nội",
        status=Order.Status.PENDING,
        total_price=product.price * 2,
    )
    OrderItem.objects.create(
        order=order,
        product=product,
        quantity=2,
        unit_price=product.price,
    )
    return order