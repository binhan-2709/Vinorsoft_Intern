"""config/urls.py — URL routing chính."""
from django.contrib import admin
from django.urls import include, path
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

urlpatterns = [
    # Django Admin  (Day 8)
    path("admin/", admin.site.urls),

    # API v1
    path("api/v1/", include([
        # Auth — JWT  (Day 9)
        path("auth/token/", TokenObtainPairView.as_view(), name="token_obtain"),
        path("auth/token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
        path("auth/", include("apps.users.urls")),

        # Apps
        path("inventory/", include("apps.inventory.urls")),   # Day 8, 9
        path("cart/", include("apps.cart.urls")),              # Day 10
        path("orders/", include("apps.orders.urls")),          # Day 11, 12
    ])),

    # API Docs  (Day 9)
    path("api/schema/", SpectacularAPIView.as_view(), name="schema"),
    path("api/docs/", SpectacularSwaggerView.as_view(url_name="schema"), name="swagger-ui"),
]