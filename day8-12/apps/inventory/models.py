"""
apps/inventory/models.py — Sản phẩm và danh mục.

Day 8: ORM nâng cao — Manager tùy chỉnh, Meta, __str__, property.
Day 10: One-to-Many relationship (Category → Product).
"""
from django.db import models
from django.utils.text import slugify


class Category(models.Model):
    """Danh mục sản phẩm — One-to-Many với Product."""

    name = models.CharField(max_length=100, unique=True, verbose_name="Tên danh mục")
    slug = models.SlugField(max_length=120, unique=True, blank=True)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "categories"
        verbose_name = "Danh mục"
        verbose_name_plural = "Danh mục"
        ordering = ["name"]

    def save(self, *args, **kwargs) -> None:
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self) -> str:
        return self.name


# ── Custom QuerySet (Day 8) ───────────────────────────────────────────
class ProductQuerySet(models.QuerySet):
    """QuerySet tuỳ chỉnh — dùng như: Product.objects.in_stock()."""

    def in_stock(self) -> "ProductQuerySet":
        return self.filter(stock__gt=0, is_active=True)

    def by_category(self, slug: str) -> "ProductQuerySet":
        return self.filter(category__slug=slug)

    def with_category(self) -> "ProductQuerySet":
        """select_related để tránh N+1 query. Day 10."""
        return self.select_related("category")


# ── class ProductManager đã được xóa bỏ ─────────────────────────────────


class Product(models.Model):
    """Sản phẩm — model trung tâm của inventory."""

    category = models.ForeignKey(
        Category,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="products",   # Day 10: category.products.all()
        verbose_name="Danh mục",
    )
    name = models.CharField(max_length=200, verbose_name="Tên sản phẩm")
    slug = models.SlugField(max_length=220, unique=True, blank=True)
    description = models.TextField(blank=True)
    price = models.DecimalField(max_digits=12, decimal_places=2, verbose_name="Giá")
    stock = models.PositiveIntegerField(default=0, verbose_name="Tồn kho")
    image = models.ImageField(upload_to="products/", null=True, blank=True)
    is_active = models.BooleanField(default=True, verbose_name="Hiển thị")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    # ✅ Custom manager đã được sửa đổi theo Cách 2
    objects = ProductQuerySet.as_manager()

    class Meta:
        db_table = "products"
        verbose_name = "Sản phẩm"
        verbose_name_plural = "Sản phẩm"
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["slug"]),
            models.Index(fields=["is_active", "stock"]),
        ]

    def save(self, *args, **kwargs) -> None:
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self) -> str:
        return self.name

    @property
    def is_in_stock(self) -> bool:
        return self.stock > 0

    @property
    def formatted_price(self) -> str:
        return f"{self.price:,.0f}đ"