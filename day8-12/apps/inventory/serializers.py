"""
apps/inventory/serializers.py — DRF Serializers.

FIX: thêm 'category_id' vào fields của ProductDetailSerializer.
"""
from rest_framework import serializers

from .models import Category, Product


class CategorySerializer(serializers.ModelSerializer):
    product_count = serializers.SerializerMethodField()

    class Meta:
        model = Category
        fields = ("id", "name", "slug", "description", "product_count")
        read_only_fields = ("slug",)

    def get_product_count(self, obj: Category) -> int:
        return obj.products.filter(is_active=True).count()


class ProductSerializer(serializers.ModelSerializer):
    """Dùng cho list — thông tin rút gọn."""
    category_name = serializers.CharField(source="category.name", read_only=True)
    is_in_stock = serializers.BooleanField(read_only=True)

    class Meta:
        model = Product
        fields = (
            "id", "name", "slug", "price",
            "stock", "is_in_stock", "is_active",
            "category", "category_name", "image",
            "created_at",
        )
        read_only_fields = ("slug", "created_at")


class ProductDetailSerializer(serializers.ModelSerializer):
    """Dùng cho detail — thêm description và category đầy đủ."""
    category = CategorySerializer(read_only=True)
    # FIX: category_id phải có trong fields
    category_id = serializers.PrimaryKeyRelatedField(
        queryset=Category.objects.all(),
        source="category",
        write_only=True,
        required=False,
        allow_null=True,
    )
    is_in_stock = serializers.BooleanField(read_only=True)
    category_name = serializers.CharField(source="category.name", read_only=True)

    class Meta:
        model = Product
        fields = (
            "id", "name", "slug", "price",
            "stock", "is_in_stock", "is_active",
            "category", "category_id", "category_name",
            "image", "description",
            "created_at", "updated_at",
        )
        read_only_fields = ("slug", "created_at", "updated_at")