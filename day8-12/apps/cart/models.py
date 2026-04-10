"""
apps/cart/models.py — Giỏ hàng.

Day 10: One-to-One (User ↔ Cart), One-to-Many (Cart → CartItem),
        ForeignKey (CartItem → Product), prefetch_related.
"""
from decimal import Decimal

from django.conf import settings
from django.db import models


class Cart(models.Model):
    """
    Giỏ hàng — One-to-One với User.
    Mỗi user chỉ có 1 giỏ hàng, tự tạo khi cần.
    """
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="cart",
        verbose_name="Người dùng",
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "carts"
        verbose_name = "Giỏ hàng"

    def __str__(self) -> str:
        return f"Giỏ hàng của {self.user.email}"

    @property
    def total_price(self) -> Decimal:
        """Tổng tiền — dùng prefetch_related để tránh N+1. Day 10."""
        return sum(item.subtotal for item in self.items.all())

    @property
    def total_items(self) -> int:
        return sum(item.quantity for item in self.items.all())

    def clear(self) -> None:
        self.items.all().delete()


class CartItem(models.Model):
    """
    Một dòng trong giỏ hàng.
    Day 10: ForeignKey tới Cart và Product.
    """
    cart = models.ForeignKey(
        Cart,
        on_delete=models.CASCADE,
        related_name="items",
        verbose_name="Giỏ hàng",
    )
    product = models.ForeignKey(
        "inventory.Product",
        on_delete=models.CASCADE,
        related_name="cart_items",
        verbose_name="Sản phẩm",
    )
    quantity = models.PositiveIntegerField(default=1, verbose_name="Số lượng")
    added_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "cart_items"
        verbose_name = "Sản phẩm trong giỏ"
        unique_together = ("cart", "product")   # Mỗi sản phẩm chỉ 1 dòng

    def __str__(self) -> str:
        return f"{self.product.name} x{self.quantity}"

    @property
    def subtotal(self) -> Decimal:
        return self.product.price * self.quantity