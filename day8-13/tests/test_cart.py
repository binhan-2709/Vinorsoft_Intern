"""
tests/test_cart.py — Unit tests cho Cart module.

Day 13: test business logic, edge cases, auth requirements.
"""
import pytest
from apps.cart.models import Cart, CartItem


@pytest.mark.django_db
class TestCartModel:
    """Test Cart model."""

    def test_cart_created_for_user(self, customer_user):
        """Tạo giỏ hàng cho user."""
        cart = Cart.objects.create(user=customer_user)
        assert cart.user == customer_user

    def test_total_price_empty_cart(self, customer_user):
        """Giỏ hàng trống có tổng = 0."""
        cart = Cart.objects.create(user=customer_user)
        assert cart.total_price == 0

    def test_total_price_with_items(self, cart_with_item, product):
        """Tổng tiền = đơn giá × số lượng."""
        expected = product.price * 2
        assert cart_with_item.total_price == expected

    def test_total_items(self, cart_with_item):
        """Tổng số lượng sản phẩm đúng."""
        assert cart_with_item.total_items == 2

    def test_clear_removes_all_items(self, cart_with_item):
        """clear() xoá toàn bộ sản phẩm trong giỏ."""
        cart_with_item.clear()
        assert cart_with_item.items.count() == 0

    def test_unique_together_cart_product(self, db, customer_user, product):
        """Mỗi sản phẩm chỉ có 1 dòng trong giỏ."""
        from django.db import IntegrityError
        cart = Cart.objects.create(user=customer_user)
        CartItem.objects.create(cart=cart, product=product, quantity=1)
        with pytest.raises(IntegrityError):
            CartItem.objects.create(cart=cart, product=product, quantity=2)


@pytest.mark.django_db
class TestCartAPI:
    """Test Cart API endpoints."""

    def test_view_cart_requires_auth(self, api_client):
        """Chưa đăng nhập không xem được giỏ → 401."""
        res = api_client.get("/api/v1/cart/")
        assert res.status_code == 401

    def test_view_empty_cart(self, auth_client):
        """Xem giỏ hàng trống."""
        res = auth_client.get("/api/v1/cart/")
        assert res.status_code == 200
        assert res.data["total_items"] == 0

    def test_add_product_to_cart(self, auth_client, product):
        """Thêm sản phẩm vào giỏ thành công."""
        res = auth_client.post("/api/v1/cart/add/", {
            "product_id": product.id,
            "quantity": 1,
        }, format="json")
        assert res.status_code == 200
        assert res.data["quantity"] == 1

    def test_add_same_product_increases_quantity(self, auth_client, product):
        """Thêm cùng sản phẩm 2 lần → cộng số lượng."""
        auth_client.post("/api/v1/cart/add/", {"product_id": product.id, "quantity": 1}, format="json")
        auth_client.post("/api/v1/cart/add/", {"product_id": product.id, "quantity": 2}, format="json")

        res = auth_client.get("/api/v1/cart/")
        assert res.data["total_items"] == 3

    def test_add_out_of_stock_product_fails(self, auth_client, out_of_stock_product):
        """Thêm sản phẩm hết hàng → 400."""
        res = auth_client.post("/api/v1/cart/add/", {
            "product_id": out_of_stock_product.id,
            "quantity": 1,
        }, format="json")
        assert res.status_code == 400
        assert "kho" in res.data["detail"].lower()

    def test_add_nonexistent_product_fails(self, auth_client):
        """Thêm sản phẩm không tồn tại → 404."""
        res = auth_client.post("/api/v1/cart/add/", {
            "product_id": 99999,
            "quantity": 1,
        }, format="json")
        assert res.status_code == 404

    def test_add_quantity_exceeds_stock_fails(self, auth_client, product):
        """Thêm số lượng vượt tồn kho → 400."""
        res = auth_client.post("/api/v1/cart/add/", {
            "product_id": product.id,
            "quantity": product.stock + 100,
        }, format="json")
        assert res.status_code == 400

    def test_clear_cart(self, auth_client, product):
        """Xoá toàn bộ giỏ hàng."""
        auth_client.post("/api/v1/cart/add/", {"product_id": product.id, "quantity": 1}, format="json")
        res = auth_client.delete("/api/v1/cart/clear/")
        assert res.status_code == 200

        cart_res = auth_client.get("/api/v1/cart/")
        assert cart_res.data["total_items"] == 0