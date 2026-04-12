"""apps/inventory/urls.py — Router tự tạo URL từ ViewSet. Day 9."""
from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import CategoryViewSet, ProductViewSet

router = DefaultRouter()
router.register("categories", CategoryViewSet, basename="category")
router.register("products", ProductViewSet, basename="product")

urlpatterns = [path("", include(router.urls))]