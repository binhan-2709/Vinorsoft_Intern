"""apps/cart/admin.py"""
from django.contrib import admin
from .models import Cart, CartItem


class CartItemInline(admin.TabularInline):
    model = CartItem
    extra = 0
    readonly_fields = ("subtotal",)

    def subtotal(self, obj: CartItem) -> str:
        return obj.formatted_subtotal if hasattr(obj, "formatted_subtotal") else f"{obj.subtotal:,.0f}đ"


@admin.register(Cart)
class CartAdmin(admin.ModelAdmin):
    list_display = ("user", "total_items", "total_price", "updated_at")
    inlines = [CartItemInline]
    readonly_fields = ("total_price", "total_items")