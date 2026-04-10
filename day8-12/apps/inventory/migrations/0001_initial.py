"""
apps/inventory/migrations/0001_initial.py
"""
import django.db.models.deletion
import django.db.models.manager
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="Category",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("name", models.CharField(max_length=100, unique=True, verbose_name="Tên danh mục")),
                ("slug", models.SlugField(blank=True, max_length=120, unique=True)),
                ("description", models.TextField(blank=True)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
            ],
            options={
                "verbose_name": "Danh mục",
                "verbose_name_plural": "Danh mục",
                "db_table": "categories",
                "ordering": ["name"],
            },
        ),
        migrations.CreateModel(
            name="Product",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("name", models.CharField(max_length=200, verbose_name="Tên sản phẩm")),
                ("slug", models.SlugField(blank=True, max_length=220, unique=True)),
                ("description", models.TextField(blank=True)),
                ("price", models.DecimalField(decimal_places=2, max_digits=12, verbose_name="Giá")),
                ("stock", models.PositiveIntegerField(default=0, verbose_name="Tồn kho")),
                ("image", models.ImageField(blank=True, null=True, upload_to="products/")),
                ("is_active", models.BooleanField(default=True, verbose_name="Hiển thị")),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("category", models.ForeignKey(
                    blank=True,
                    null=True,
                    on_delete=django.db.models.deletion.SET_NULL,
                    related_name="products",
                    to="inventory.category",
                    verbose_name="Danh mục",
                )),
            ],
            options={
                "verbose_name": "Sản phẩm",
                "verbose_name_plural": "Sản phẩm",
                "db_table": "products",
                "ordering": ["-created_at"],
            },
            managers=[
                ("objects", django.db.models.manager.Manager()),
            ],
        ),
        migrations.AddIndex(
            model_name="product",
            index=models.Index(fields=["slug"], name="products_slug_idx"),
        ),
        migrations.AddIndex(
            model_name="product",
            index=models.Index(fields=["is_active", "stock"], name="products_active_stock_idx"),
        ),
    ]