"""
apps/inventory/views.py — DRF ViewSets.

Day 9: ModelViewSet, GenericAPIView, filtering, searching, ordering.
"""
import django_filters
from rest_framework import filters, permissions, viewsets
from rest_framework.decorators import action
from rest_framework.request import Request
from rest_framework.response import Response

from .models import Category, Product
from .serializers import CategorySerializer, ProductDetailSerializer, ProductSerializer


# ── Filter class (Day 9) ──────────────────────────────────────────────
class ProductFilter(django_filters.FilterSet):
    min_price = django_filters.NumberFilter(field_name="price", lookup_expr="gte")
    max_price = django_filters.NumberFilter(field_name="price", lookup_expr="lte")
    in_stock = django_filters.BooleanFilter(method="filter_in_stock")

    class Meta:
        model = Product
        fields = ["category", "is_active"]

    def filter_in_stock(self, queryset, name, value):  # noqa: ANN001
        if value:
            return queryset.filter(stock__gt=0)
        return queryset


# ── ViewSets (Day 9) ──────────────────────────────────────────────────
class CategoryViewSet(viewsets.ModelViewSet):
    """
    CRUD danh mục — tự động có list, create, retrieve, update, destroy.
    Day 9: ModelViewSet = 5 endpoints chỉ với ~10 dòng code.
    """
    queryset = Category.objects.prefetch_related("products")
    serializer_class = CategorySerializer
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,)
    filter_backends = (filters.SearchFilter, filters.OrderingFilter)
    search_fields = ("name",)
    ordering_fields = ("name", "created_at")
    lookup_field = "slug"


class ProductViewSet(viewsets.ModelViewSet):
    """
    CRUD sản phẩm với filter, search, ordering.
    Day 10: select_related tránh N+1 query.
    """
    queryset = Product.objects.with_category().filter(is_active=True)
    filter_backends = (
        django_filters.rest_framework.DjangoFilterBackend,
        filters.SearchFilter,
        filters.OrderingFilter,
    )
    filterset_class = ProductFilter
    search_fields = ("name", "description")
    ordering_fields = ("price", "created_at", "stock")
    lookup_field = "slug"

    def get_serializer_class(self):  # noqa: ANN201
        if self.action == "retrieve":
            return ProductDetailSerializer
        return ProductSerializer

    def get_permissions(self):  # noqa: ANN201
        """Chỉ admin/staff mới được tạo, sửa, xoá."""
        if self.action in ("create", "update", "partial_update", "destroy"):
            return [permissions.IsAdminUser()]
        return [permissions.AllowAny()]

    def get_queryset(self):  # noqa: ANN201
        """Admin thấy cả sản phẩm ẩn."""
        if self.request.user.is_staff:
            return Product.objects.with_category()
        return Product.objects.with_category().filter(is_active=True)

    @action(detail=False, methods=["get"])
    def in_stock(self, request: Request) -> Response:
        """GET /api/v1/inventory/products/in_stock/ — Sản phẩm còn hàng."""
        qs = Product.objects.in_stock().with_category()
        page = self.paginate_queryset(qs)
        serializer = ProductSerializer(page, many=True)
        return self.get_paginated_response(serializer.data)