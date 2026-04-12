"""
apps/orders/views.py — Đặt hàng và quản lý đơn.

Day 12: Checkout từ giỏ hàng → tạo Order + OrderItems → Signal → Celery email.
"""
from django.db import transaction
from rest_framework import generics, permissions, status
from rest_framework.decorators import action
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet

from apps.cart.models import Cart
from .models import Order, OrderItem
from .serializers import (
    CreateOrderSerializer,
    OrderSerializer,
    UpdateOrderStatusSerializer,
)


class OrderViewSet(ModelViewSet):
    """
    Day 12: Full order management.

    - POST /orders/checkout/ → Tạo đơn từ giỏ hàng
    - GET  /orders/          → Danh sách đơn của user
    - GET  /orders/{id}/     → Chi tiết đơn
    - POST /orders/{id}/cancel/ → Huỷ đơn
    - POST /orders/{id}/status/ → Admin đổi trạng thái
    """
    serializer_class = OrderSerializer
    permission_classes = (permissions.IsAuthenticated,)
    http_method_names = ["get", "post", "head", "options"]

    def get_queryset(self):  # noqa: ANN201
        qs = Order.objects.select_related("user").prefetch_related("items__product")
        # Admin thấy tất cả, user chỉ thấy của mình
        if self.request.user.is_staff:
            return qs
        return qs.filter(user=self.request.user)

    @action(detail=False, methods=["post"])
    def checkout(self, request: Request) -> Response:
        """
        POST /api/v1/orders/checkout/ — Đặt hàng từ giỏ hàng hiện tại.

        Day 12: Dùng transaction.atomic() đảm bảo tính toàn vẹn dữ liệu.
        """
        serializer = CreateOrderSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            cart = Cart.objects.prefetch_related("items__product").get(user=request.user)
        except Cart.DoesNotExist:
            return Response({"detail": "Giỏ hàng trống."}, status=400)

        if not cart.items.exists():
            return Response({"detail": "Giỏ hàng trống."}, status=400)

        with transaction.atomic():
            # Kiểm tra tồn kho và trừ stock
            for item in cart.items.select_related("product"):
                if item.product.stock < item.quantity:
                    return Response(
                        {"detail": f"Sản phẩm '{item.product.name}' không đủ hàng."},
                        status=400,
                    )
                item.product.stock -= item.quantity
                item.product.save(update_fields=["stock"])

            # Tạo Order
            order = Order.objects.create(
                user=request.user,
                shipping_address=serializer.validated_data["shipping_address"],
                note=serializer.validated_data.get("note", ""),
            )

            # Tạo OrderItem — snapshot giá tại thời điểm đặt
            order_items = [
                OrderItem(
                    order=order,
                    product=item.product,
                    quantity=item.quantity,
                    unit_price=item.product.price,   # snapshot giá
                )
                for item in cart.items.select_related("product")
            ]
            OrderItem.objects.bulk_create(order_items)

            # Tính tổng tiền
            order.calculate_total()

            # Xoá giỏ hàng
            cart.clear()

        # Signal post_save tự động kích hoạt → Celery gửi email (Day 11)
        return Response(OrderSerializer(order).data, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=["post"])
    def cancel(self, request: Request, pk=None) -> Response:  # noqa: ANN001
        """POST /orders/{id}/cancel/ — Khách huỷ đơn."""
        order = self.get_object()
        if not order.can_cancel():
            return Response({"detail": "Không thể huỷ đơn ở trạng thái này."}, status=400)
        order.status = Order.Status.CANCELLED
        order.save()
        return Response({"detail": "Đã huỷ đơn hàng."})

    @action(detail=True, methods=["post"], permission_classes=[permissions.IsAdminUser])
    def update_status(self, request: Request, pk=None) -> Response:  # noqa: ANN001
        """POST /orders/{id}/update_status/ — Admin đổi trạng thái đơn."""
        order = self.get_object()
        serializer = UpdateOrderStatusSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        order.status = serializer.validated_data["status"]
        order.save()
        return Response(OrderSerializer(order).data)