"""apps/orders/serializers.py — Day 9, 12."""
from rest_framework import serializers

from apps.inventory.serializers import ProductSerializer
from .models import Order, OrderItem


class OrderItemSerializer(serializers.ModelSerializer):
    product = ProductSerializer(read_only=True)
    subtotal = serializers.DecimalField(max_digits=12, decimal_places=2, read_only=True)

    class Meta:
        model = OrderItem
        fields = ("id", "product", "quantity", "unit_price", "subtotal")


class OrderSerializer(serializers.ModelSerializer):
    """Day 10: Nested items trong order response."""
    items = OrderItemSerializer(many=True, read_only=True)
    status_display = serializers.CharField(source="get_status_display", read_only=True)
    user_email = serializers.CharField(source="user.email", read_only=True)

    class Meta:
        model = Order
        fields = (
            "id", "user_email", "status", "status_display",
            "total_price", "shipping_address", "note",
            "items", "created_at", "updated_at",
        )
        read_only_fields = ("id", "total_price", "status", "created_at", "updated_at")


class CreateOrderSerializer(serializers.Serializer):
    """Day 12: Tạo đơn từ giỏ hàng hiện tại."""
    shipping_address = serializers.CharField(min_length=10)
    note = serializers.CharField(required=False, allow_blank=True, default="")


class UpdateOrderStatusSerializer(serializers.Serializer):
    """Chỉ admin/staff mới được đổi status."""
    status = serializers.ChoiceField(choices=Order.Status.choices)