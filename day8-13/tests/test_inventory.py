"""
tests/test_inventory.py — Unit tests cho Inventory module.

Day 13: pytest-django, Mocking, coverage > 80%.
Kiểm tra: models, custom manager, API endpoints, permissions.
"""
import pytest
from django.urls import reverse
from unittest.mock import patch, MagicMock

from apps.inventory.models import Category, Product


# ══════════════════════════════════════════════════════════════════════
# MODEL TESTS
# ══════════════════════════════════════════════════════════════════════

class TestCategoryModel:
    """Test Category model."""

    def test_slug_auto_generated(self, db):
        """Slug tự động tạo từ tên khi save."""
        cat = Category.objects.create(name="Điện Thoại")
        assert cat.slug == "dien-thoai"

    def test_slug_not_overwritten(self, db):
        """Slug không bị ghi đè nếu đã có."""
        cat = Category.objects.create(name="Điện Thoại", slug="custom-slug")
        assert cat.slug == "custom-slug"

    def test_str_returns_name(self, category):
        """__str__ trả về tên danh mục."""
        assert str(category) == "Điện tử"

    def test_unique_name(self, db):
        """Không cho phép 2 danh mục cùng tên."""
        from django.db import IntegrityError
        Category.objects.create(name="Trùng tên")
        with pytest.raises(IntegrityError):
            Category.objects.create(name="Trùng tên")


class TestProductModel:
    """Test Product model."""

    def test_slug_auto_generated(self, db, category):
        """Slug tự tạo từ tên sản phẩm."""
        p = Product.objects.create(name="MacBook Pro", price=45_000_000, category=category)
        assert p.slug == "macbook-pro"

    def test_is_in_stock_true(self, product):
        """is_in_stock = True khi còn hàng."""
        assert product.is_in_stock is True

    def test_is_in_stock_false(self, out_of_stock_product):
        """is_in_stock = False khi hết hàng."""
        assert out_of_stock_product.is_in_stock is False

    def test_formatted_price(self, product):
        """formatted_price hiển thị đúng định dạng."""
        assert "đ" in product.formatted_price

    def test_str_returns_name(self, product):
        assert str(product) == "iPhone 15 Pro"


# ══════════════════════════════════════════════════════════════════════
# CUSTOM MANAGER TESTS
# ══════════════════════════════════════════════════════════════════════

class TestProductManager:
    """Test ProductManager và ProductQuerySet."""

    def test_in_stock_excludes_out_of_stock(self, db, product, out_of_stock_product):
        """in_stock() chỉ trả về sản phẩm còn hàng."""
        qs = Product.objects.in_stock()
        assert product in qs
        assert out_of_stock_product not in qs

    def test_in_stock_excludes_inactive(self, db, product, inactive_product):
        """in_stock() không trả về sản phẩm đã ẩn."""
        qs = Product.objects.in_stock()
        assert inactive_product not in qs

    def test_with_category_uses_select_related(self, db, product):
        """with_category() dùng select_related — không gây thêm query."""
        from django.test.utils import CaptureQueriesContext
        from django.db import connection

        qs = Product.objects.with_category()
        with CaptureQueriesContext(connection) as ctx:
            # Truy cập category không tạo query mới
            _ = [p.category for p in qs]

        # select_related → chỉ 1 query JOIN, không N+1
        assert len(ctx.captured_queries) <= 1


# ══════════════════════════════════════════════════════════════════════
# API ENDPOINT TESTS
# ══════════════════════════════════════════════════════════════════════

@pytest.mark.django_db
class TestProductAPI:
    """Test Product API endpoints."""

    def test_list_products_no_auth(self, api_client, product):
        """Ai cũng xem được danh sách sản phẩm."""
        res = api_client.get("/api/v1/inventory/products/")
        assert res.status_code == 200
        assert res.data["count"] >= 1

    def test_list_products_filter_in_stock(self, api_client, product, out_of_stock_product):
        """Lọc sản phẩm còn hàng."""
        res = api_client.get("/api/v1/inventory/products/?in_stock=true")
        assert res.status_code == 200
        slugs = [p["slug"] for p in res.data["results"]]
        assert product.slug in slugs
        assert out_of_stock_product.slug not in slugs

    def test_list_products_filter_by_price(self, api_client, db, category):
        """Lọc sản phẩm theo khoảng giá."""
        Product.objects.create(name="Rẻ", price=50_000, stock=5, category=category)
        Product.objects.create(name="Đắt", price=50_000_000, stock=5, category=category)

        res = api_client.get("/api/v1/inventory/products/?min_price=40000&max_price=100000")
        assert res.status_code == 200
        names = [p["name"] for p in res.data["results"]]
        assert "Rẻ" in names
        assert "Đắt" not in names

    def test_retrieve_product_by_slug(self, api_client, product):
        """Lấy chi tiết sản phẩm theo slug."""
        res = api_client.get(f"/api/v1/inventory/products/{product.slug}/")
        assert res.status_code == 200
        assert res.data["name"] == product.name

    def test_retrieve_nonexistent_product_returns_404(self, api_client):
        """Slug không tồn tại trả về 404."""
        res = api_client.get("/api/v1/inventory/products/khong-ton-tai/")
        assert res.status_code == 404

    def test_create_product_requires_admin(self, auth_client, category):
        """Khách hàng không tạo được sản phẩm → 403."""
        res = auth_client.post("/api/v1/inventory/products/", {
            "name": "Test Product",
            "price": 100_000,
            "stock": 10,
        }, format="json")
        assert res.status_code == 403

    def test_create_product_as_admin(self, admin_client, category):
        """Admin tạo được sản phẩm → 201."""
        res = admin_client.post("/api/v1/inventory/products/", {
            "name": "New Product",
            "price": 500_000,
            "stock": 20,
            "category_id": category.id,
        }, format="json")
        assert res.status_code == 201
        assert res.data["name"] == "New Product"

    def test_in_stock_endpoint(self, api_client, product, out_of_stock_product):
        """Custom action in_stock/ chỉ trả về sản phẩm còn hàng."""
        res = api_client.get("/api/v1/inventory/products/in_stock/")
        assert res.status_code == 200
        slugs = [p["slug"] for p in res.data["results"]]
        assert product.slug in slugs
        assert out_of_stock_product.slug not in slugs


@pytest.mark.django_db
class TestCategoryAPI:
    """Test Category API endpoints."""

    def test_list_categories(self, api_client, category):
        """Ai cũng xem được danh mục."""
        res = api_client.get("/api/v1/inventory/categories/")
        assert res.status_code == 200

    def test_create_category_as_admin(self, admin_client):
        """Admin tạo danh mục thành công."""
        res = admin_client.post("/api/v1/inventory/categories/", {
            "name": "Thời trang",
            "description": "Quần áo các loại",
        }, format="json")
        assert res.status_code == 201
        assert res.data["name"] == "Thời trang"

    def test_create_category_unauthenticated(self, api_client):
        """Chưa đăng nhập không tạo được danh mục → 401."""
        res = api_client.post("/api/v1/inventory/categories/", {
            "name": "Test",
        }, format="json")
        assert res.status_code == 401


# ══════════════════════════════════════════════════════════════════════
# MOCKING TESTS
# ══════════════════════════════════════════════════════════════════════

class TestInventoryWithMocking:
    """
    Day 13: Mock external dependencies.
    """

    @patch("apps.inventory.models.slugify")
    def test_slug_uses_slugify(self, mock_slugify, db, category):
        """Kiểm tra slugify được gọi khi tạo product mới."""
        mock_slugify.return_value = "mocked-slug"
        p = Product(name="Test", price=100, category=category)
        p.save()
        mock_slugify.assert_called_once_with("Test")

    def test_product_manager_returns_queryset(self, db):
        """ProductManager.in_stock() trả về QuerySet."""
        from django.db.models.query import QuerySet
        result = Product.objects.in_stock()
        assert isinstance(result, QuerySet)