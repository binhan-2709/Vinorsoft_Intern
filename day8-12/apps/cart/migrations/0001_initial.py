"""
apps/cart/migrations/0001_initial.py
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
            name="Cart",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("user", models.OneToOneField(
                    on_delete=django.db.models.deletion.CASCADE,
                    related_name="cart",
                    to=settings.AUTH_USER_MODEL,
                    verbose_name="Người dùng",
                )),
            ],
            options={
                "verbose_name": "Giỏ hàng",
                "db_table": "carts",
            },
        ),
        migrations.CreateModel(
            name="CartItem",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("quantity", models.PositiveIntegerField(default=1, verbose_name="Số lượng")),
                ("added_at", models.DateTimeField(auto_now_add=True)),
                ("cart", models.ForeignKey(
                    on_delete=django.db.models.deletion.CASCADE,
                    related_name="items",
                    to="cart.cart",
                    verbose_name="Giỏ hàng",
                )),
                ("product", models.ForeignKey(
                    on_delete=django.db.models.deletion.CASCADE,
                    related_name="cart_items",
                    to="inventory.product",
                    verbose_name="Sản phẩm",
                )),
            ],
            options={
                "verbose_name": "Sản phẩm trong giỏ",
                "db_table": "cart_items",
            },
        ),
        migrations.AlterUniqueTogether(
            name="cartitem",
            unique_together={("cart", "product")},
        ),
    ]