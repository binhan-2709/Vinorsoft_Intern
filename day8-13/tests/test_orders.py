"""
tests/test_orders.py — Unit tests cho Orders module.

Day 13: Mock Celery tasks, test signals, test checkout flow.
"""
import pytest
from unittest.mock import patch, call
from decimal import Decimal
from django.core import mail

from apps.cart.models import Cart, CartItem
from apps.orders.models import Order, OrderItem
from apps.orders.tasks import send_order_confirmation_email, restore_stock_on_cancel


@pytest.mark.django_db
class TestOrderModel:
    """Test Order model."""

    def test_str_representation(self, pending_order, customer_user):
        assert str(pending_order).__contains__(customer_user.email)

    def test_can_cancel_when_pending(self, pending_order):
        """Đơn pending có thể huỷ."""
        assert pending_order.can_cancel() is True

    def test_can_cancel_when_confirmed(self, pending_order):
        """Đơn confirmed có thể huỷ."""
        pending_order.status = Order.Status.CONFIRMED
        assert pending_order.can_cancel() is True

    def test_cannot_cancel_when_shipping(self, pending_order):
        """Đơn đang giao không thể huỷ."""
        pending_order.status = Order.Status.SHIPPING
        assert pending_order.can_cancel() is False

    def test_cannot_cancel_when_delivered(self, pending_order):
        """Đơn đã giao không thể huỷ."""
        pending_order.status = Order.Status.DELIVERED
        assert pending_order.can_cancel() is False


@pytest.mark.django_db
class TestCheckoutAPI:
    """Test checkout flow end-to-end."""

    def test_checkout_requires_auth(self, api_client):
        """Chưa đăng nhập không đặt hàng được → 401."""
        res = api_client.post("/api/v1/orders/checkout/", {
            "shipping_address": "Test address"
        }, format="json")
        assert res.status_code == 401

    @patch("apps.orders.tasks.send_order_confirmation_email.delay")
    def test_checkout_success(self, mock_email, auth_client, customer_user, product):
        """Checkout thành công — tạo Order, trừ stock, gọi Celery task."""
        # Thêm sản phẩm vào giỏ
        cart = Cart.objects.create(user=customer_user)
        CartItem.objects.create(cart=cart, product=product, quantity=2)
        initial_stock = product.stock

        res = auth_client.post("/api/v1/orders/checkout/", {
            "shipping_address": "123 Đường ABC, Hà Nội",
            "note": "Giao buổi sáng",
        }, format="json")

        assert res.status_code == 201
        assert res.data["status"] == "pending"
        assert Decimal(res.data["total_price"]) == product.price * 2

        # Kiểm tra stock đã bị trừ
        product.refresh_from_db()
        assert product.stock == initial_stock - 2

        # Kiểm tra giỏ hàng đã được xoá
        assert not CartItem.objects.filter(cart=cart).exists()

        # Kiểm tra Celery task được gọi (Day 13: Mocking)
        mock_email.assert_called_once()

    def test_checkout_empty_cart_fails(self, auth_client):
        """Checkout với giỏ trống → 400."""
        res = auth_client.post("/api/v1/orders/checkout/", {
            "shipping_address": "Test address",
        }, format="json")
        assert res.status_code == 400

    @patch("apps.orders.tasks.send_order_confirmation_email.delay")
    def test_checkout_insufficient_stock_fails(self, mock_email, auth_client, customer_user, product):
        """Checkout khi không đủ hàng → 400, không tạo Order."""
        cart = Cart.objects.create(user=customer_user)
        CartItem.objects.create(cart=cart, product=product, quantity=product.stock + 100)

        res = auth_client.post("/api/v1/orders/checkout/", {
            "shipping_address": "Test address",
        }, format="json")

        assert res.status_code == 400
        assert Order.objects.filter(user=customer_user).count() == 0
        mock_email.assert_not_called()

    def test_list_orders_only_own(self, auth_client, another_user, customer_user, pending_order, db):
        """User chỉ thấy đơn của mình."""
        # Tạo đơn của user khác
        Order.objects.create(
            user=another_user,
            shipping_address="Another address",
            total_price=100_000,
        )

        res = auth_client.get("/api/v1/orders/")
        assert res.status_code == 200
        order_ids = [o["id"] for o in res.data["results"]]
        assert pending_order.id in order_ids
        # Không thấy đơn của user khác
        for order in res.data["results"]:
            assert order["user_email"] == customer_user.email

    def test_cancel_pending_order(self, auth_client, pending_order):
        """Huỷ đơn pending thành công."""
        res = auth_client.post(f"/api/v1/orders/{pending_order.id}/cancel/")
        assert res.status_code == 200
        pending_order.refresh_from_db()
        assert pending_order.status == Order.Status.CANCELLED

    @patch("apps.orders.tasks.send_order_confirmation_email.delay")
    def test_cancel_shipped_order_fails(self, mock_email, auth_client, pending_order):
        """Không thể huỷ đơn đang giao → 400."""
        pending_order.status = Order.Status.SHIPPING
        pending_order.save()

        res = auth_client.post(f"/api/v1/orders/{pending_order.id}/cancel/")
        assert res.status_code == 400

    def test_admin_can_update_status(self, admin_client, pending_order):
        """Admin đổi trạng thái đơn thành công."""
        res = admin_client.post(f"/api/v1/orders/{pending_order.id}/update_status/", {
            "status": "confirmed"
        }, format="json")
        assert res.status_code == 200
        assert res.data["status"] == "confirmed"

    def test_customer_cannot_update_status(self, auth_client, pending_order):
        """Khách hàng không được đổi trạng thái → 403."""
        res = auth_client.post(f"/api/v1/orders/{pending_order.id}/update_status/", {
            "status": "confirmed"
        }, format="json")
        assert res.status_code == 403


@pytest.mark.django_db
class TestOrderSignals:
    """
    Day 13: Test Django Signals với mock.
    """

    @patch("apps.orders.tasks.send_order_confirmation_email.delay")
    def test_signal_fires_on_order_create(self, mock_task, customer_user):
        """post_save signal gọi Celery task khi tạo Order mới."""
        order = Order.objects.create(
            user=customer_user,
            shipping_address="Test address",
            total_price=100_000,
        )
        mock_task.assert_called_once_with(order.pk)

    @patch("apps.orders.tasks.send_order_confirmation_email.delay")
    def test_signal_not_fired_on_update(self, mock_task, pending_order):
        """Signal không gọi lại khi update Order."""
        pending_order.status = Order.Status.CONFIRMED
        pending_order.save()
        # Chỉ gọi 1 lần lúc tạo (trong fixture), không gọi thêm lúc update
        mock_task.assert_not_called()

    @patch("apps.orders.tasks.restore_stock_on_cancel.delay")
    def test_signal_restore_stock_on_cancel(self, mock_restore, pending_order):
        """pre_save signal gọi restore_stock khi huỷ đơn."""
        pending_order.status = Order.Status.CANCELLED
        pending_order.save()
        mock_restore.assert_called_once_with(pending_order.pk)
        
        
class TestCeleryTasks:
    def test_send_email_task_runs_successfully(self, db, pending_order):
        """Test hàm gửi email chạy thật sự (không dùng mock)"""
        # Gọi THẲNG hàm thật, không dùng .delay()
        send_order_confirmation_email(pending_order.id)
        
        # Django có cơ chế tự động chặn email thật trong lúc test 
        # và đưa vào hộp thư ảo (mail.outbox). Ta chỉ cần đếm số thư ở đây:
        assert len(mail.outbox) == 1
        assert mail.outbox[0].subject == f"[Shop] Xác nhận đơn hàng #{pending_order.id}"
        
    def test_restore_stock_task_runs_successfully(self, db, pending_order):
        """Test hàm hoàn kho chạy thật sự"""
        # 1. Lấy món hàng đầu tiên trong đơn và ghi nhớ số tồn kho cũ
        order_item = pending_order.items.first()
        product = order_item.product
        old_stock = product.stock

        # 2. Hủy đơn hàng và gọi thẳng hàm hoàn kho
        pending_order.status = 'cancelled'
        pending_order.save()
        restore_stock_on_cancel(pending_order.id)

        # 3. Lấy lại dữ liệu từ DB và kiểm tra xem kho đã được cộng lên chưa
        product.refresh_from_db()
        assert product.stock == old_stock + order_item.quantity