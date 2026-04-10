"""
apps/orders/models.py — Đơn hàng và chi tiết đơn hàng.

Day 11: post_save Signal sẽ trigger khi Order được tạo.
Day 12: Mini Project — Order đầy đủ với status workflow.
"""
from decimal import Decimal

from django.conf import settings
from django.db import models


class Order(models.Model):
    """Đơn hàng của khách."""

    class Status(models.TextChoices):
        PENDING = "pending", "Chờ xử lý"
        CONFIRMED = "confirmed", "Đã xác nhận"
        SHIPPING = "shipping", "Đang giao"
        DELIVERED = "delivered", "Đã giao"
        CANCELLED = "cancelled", "Đã huỷ"

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="orders",
        verbose_name="Khách hàng",
    )
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.PENDING,
        verbose_name="Trạng thái",
    )
    total_price = models.DecimalField(
        max_digits=14, decimal_places=2, default=Decimal("0"),
        verbose_name="Tổng tiền",
    )
    shipping_address = models.TextField(verbose_name="Địa chỉ giao hàng")
    note = models.TextField(blank=True, verbose_name="Ghi chú")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "orders"
        verbose_name = "Đơn hàng"
        verbose_name_plural = "Đơn hàng"
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["user", "status"]),
            models.Index(fields=["created_at"]),
        ]

    def __str__(self) -> str:
        return f"Order #{self.pk} — {self.user.email} — {self.get_status_display()}"

    def calculate_total(self) -> Decimal:
        """Tính lại tổng tiền từ các OrderItem."""
        total = sum(item.subtotal for item in self.items.all())
        self.total_price = total
        self.save(update_fields=["total_price"])
        return total

    def can_cancel(self) -> bool:
        return self.status in (self.Status.PENDING, self.Status.CONFIRMED)


class OrderItem(models.Model):
    """
    Chi tiết đơn hàng — snapshot giá lúc đặt hàng.

    Day 10/12: Many-to-One (Order → OrderItem), lưu price tại thời điểm đặt
    để không bị ảnh hưởng khi giá sản phẩm thay đổi.
    """
    order = models.ForeignKey(
        Order,
        on_delete=models.CASCADE,
        related_name="items",
        verbose_name="Đơn hàng",
    )
    product = models.ForeignKey(
        "inventory.Product",
        on_delete=models.PROTECT,
        related_name="order_items",
        verbose_name="Sản phẩm",
    )
    quantity = models.PositiveIntegerField(verbose_name="Số lượng")
    unit_price = models.DecimalField(
        max_digits=12, decimal_places=2,
        verbose_name="Đơn giá lúc đặt",
    )

    class Meta:
        db_table = "order_items"
        verbose_name = "Chi tiết đơn hàng"

    def __str__(self) -> str:
        return f"{self.product.name} x{self.quantity}"

    @property
    def subtotal(self) -> Decimal:
        return self.unit_price * self.quantity