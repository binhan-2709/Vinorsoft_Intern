"""apps/orders/apps.py — Đăng ký signals khi app khởi động. Day 11."""
from django.apps import AppConfig


class OrdersConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.orders"
    verbose_name = "Đơn hàng"

    def ready(self) -> None:
        """Import signals khi app load — bắt buộc để signals hoạt động."""
        import apps.orders.signals  # noqa: F401