"""apps/orders/admin.py — Django Admin cho đơn hàng."""
from django.contrib import admin
from django.utils.html import format_html

from .models import Order, OrderItem


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    readonly_fields = ("subtotal",)

    def subtotal(self, obj: OrderItem) -> str:
        return f"{obj.subtotal:,.0f}đ"


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "status_badge", "total_price", "created_at")
    list_filter = ("status", "created_at")
    search_fields = ("user__email", "shipping_address")
    readonly_fields = ("total_price", "created_at", "updated_at")
    inlines = [OrderItemInline]
    actions = ["mark_confirmed", "mark_shipping", "mark_delivered"]

    def get_queryset(self, request):  # noqa: ANN001, ANN201
        return super().get_queryset(request).select_related("user")

    @admin.display(description="Trạng thái")
    def status_badge(self, obj: Order) -> str:
        colors = {
            "pending": "orange",
            "confirmed": "blue",
            "shipping": "purple",
            "delivered": "green",
            "cancelled": "red",
        }
        color = colors.get(obj.status, "gray")
        return format_html(
            '<span style="color:{};font-weight:bold">{}</span>',
            color, obj.get_status_display()
        )

    @admin.action(description="Xác nhận đơn đã chọn")
    def mark_confirmed(self, request, queryset):  # noqa: ANN001
        queryset.update(status=Order.Status.CONFIRMED)

    @admin.action(description="Chuyển sang đang giao")
    def mark_shipping(self, request, queryset):  # noqa: ANN001
        queryset.update(status=Order.Status.SHIPPING)

    @admin.action(description="Đánh dấu đã giao")
    def mark_delivered(self, request, queryset):  # noqa: ANN001
        queryset.update(status=Order.Status.DELIVERED)