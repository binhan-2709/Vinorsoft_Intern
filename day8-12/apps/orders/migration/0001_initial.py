"""
apps/orders/migrations/0001_initial.py
"""
import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ("inventory", "0001_initial"),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name="Order",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("status", models.CharField(
                    choices=[
                        ("pending", "Chờ xử lý"),
                        ("confirmed", "Đã xác nhận"),
                        ("shipping", "Đang giao"),
                        ("delivered", "Đã giao"),
                        ("cancelled", "Đã huỷ"),
                    ],
                    default="pending",
                    max_length=20,
                    verbose_name="Trạng thái",
                )),
                ("total_price", models.DecimalField(
                    decimal_places=2,
                    default=0,
                    max_digits=14,
                    verbose_name="Tổng tiền",
                )),
                ("shipping_address", models.TextField(verbose_name="Địa chỉ giao hàng")),
                ("note", models.TextField(blank=True, verbose_name="Ghi chú")),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("user", models.ForeignKey(
                    on_delete=django.db.models.deletion.PROTECT,
                    related_name="orders",
                    to=settings.AUTH_USER_MODEL,
                    verbose_name="Khách hàng",
                )),
            ],
            options={
                "verbose_name": "Đơn hàng",
                "verbose_name_plural": "Đơn hàng",
                "db_table": "orders",
                "ordering": ["-created_at"],
            },
        ),
        migrations.CreateModel(
            name="OrderItem",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("quantity", models.PositiveIntegerField(verbose_name="Số lượng")),
                ("unit_price", models.DecimalField(
                    decimal_places=2,
                    max_digits=12,
                    verbose_name="Đơn giá lúc đặt",
                )),
                ("order", models.ForeignKey(
                    on_delete=django.db.models.deletion.CASCADE,
                    related_name="items",
                    to="orders.order",
                    verbose_name="Đơn hàng",
                )),
                ("product", models.ForeignKey(
                    on_delete=django.db.models.deletion.PROTECT,
                    related_name="order_items",
                    to="inventory.product",
                    verbose_name="Sản phẩm",
                )),
            ],
            options={
                "verbose_name": "Chi tiết đơn hàng",
                "db_table": "order_items",
            },
        ),
        migrations.AddIndex(
            model_name="order",
            index=models.Index(fields=["user", "status"], name="orders_user_status_idx"),
        ),
        migrations.AddIndex(
            model_name="order",
            index=models.Index(fields=["created_at"], name="orders_created_at_idx"),
        ),
    ]