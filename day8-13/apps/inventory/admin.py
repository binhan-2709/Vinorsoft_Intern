"""
apps/inventory/admin.py — Django Admin cực mạnh cho kho hàng.

Day 8: list_display, list_filter, search_fields, inline, actions.
"""
from django.contrib import admin
from django.db.models import QuerySet
from django.http import HttpRequest
from django.utils.html import format_html

from .models import Category, Product


class ProductInline(admin.TabularInline):
    """Hiển thị sản phẩm ngay trong trang danh mục."""
    model = Product
    extra = 0
    fields = ("name", "price", "stock", "is_active")
    show_change_link = True


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ("name", "slug", "product_count", "created_at")
    search_fields = ("name",)
    prepopulated_fields = {"slug": ("name",)}
    inlines = [ProductInline]

    @admin.display(description="Số sản phẩm")
    def product_count(self, obj: Category) -> int:
        return obj.products.count()


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = (
        "name", "category", "formatted_price",
        "stock", "stock_status", "is_active", "updated_at",
    )
    list_filter = ("is_active", "category")
    search_fields = ("name", "description")
    prepopulated_fields = {"slug": ("name",)}
    list_editable = ("stock", "is_active")    # Sửa trực tiếp trong danh sách
    readonly_fields = ("created_at", "updated_at")
    actions = ["mark_active", "mark_inactive"]

    # Optimized queryset — tránh N+1  (Day 10)
    def get_queryset(self, request: HttpRequest) -> QuerySet:
        return super().get_queryset(request).select_related("category")

    @admin.display(description="Giá")
    def formatted_price(self, obj: Product) -> str:
        return obj.formatted_price

    @admin.display(description="Kho", boolean=False)
    def stock_status(self, obj: Product) -> str:
        if obj.stock == 0:
            return format_html('<span style="color:red">⚠ Hết hàng</span>')
        if obj.stock < 10:
            return format_html('<span style="color:orange">⚡ Sắp hết ({})</span>', obj.stock)
        return format_html('<span style="color:green">✓ Còn hàng ({})</span>', obj.stock)

    @admin.action(description="Bật hiển thị các sản phẩm đã chọn")
    def mark_active(self, request: HttpRequest, queryset: QuerySet) -> None:
        queryset.update(is_active=True)

    @admin.action(description="Ẩn các sản phẩm đã chọn")
    def mark_inactive(self, request: HttpRequest, queryset: QuerySet) -> None:
        queryset.update(is_active=False)