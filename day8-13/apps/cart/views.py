"""
apps/cart/views.py — Giỏ hàng API.
"""
from drf_spectacular.utils import extend_schema
from rest_framework import permissions, status
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.inventory.models import Product
from .models import Cart, CartItem
from .serializers import AddToCartSerializer, CartSerializer


def get_or_create_cart(user) -> Cart:
    cart, _ = Cart.objects.get_or_create(user=user)
    return cart


class CartView(APIView):
    permission_classes = (permissions.IsAuthenticated,)

    @extend_schema(
        summary="Xem giỏ hàng",
        responses={200: CartSerializer},
        tags=["Cart"],
    )
    def get(self, request: Request) -> Response:
        """Lấy giỏ hàng hiện tại của user đang đăng nhập."""
        cart = get_or_create_cart(request.user)
        cart = Cart.objects.prefetch_related("items__product__category").get(pk=cart.pk)
        return Response(CartSerializer(cart).data)


class CartAddView(APIView):
    permission_classes = (permissions.IsAuthenticated,)

    @extend_schema(
        summary="Thêm sản phẩm vào giỏ",
        request=AddToCartSerializer,
        responses={200: {"type": "object", "properties": {"detail": {"type": "string"}, "quantity": {"type": "integer"}}}},
        tags=["Cart"],
    )
    def post(self, request: Request) -> Response:
        """Thêm sản phẩm vào giỏ hàng. Nếu đã có sẽ cộng thêm số lượng."""
        serializer = AddToCartSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        product_id = serializer.validated_data["product_id"]
        quantity = serializer.validated_data["quantity"]

        try:
            product = Product.objects.get(pk=product_id, is_active=True)
        except Product.DoesNotExist:
            return Response({"detail": "Sản phẩm không tồn tại."}, status=404)

        if product.stock < quantity:
            return Response(
                {"detail": f"Chỉ còn {product.stock} sản phẩm trong kho."},
                status=400,
            )

        cart = get_or_create_cart(request.user)

        item, created = CartItem.objects.get_or_create(
            cart=cart,
            product=product,
            defaults={"quantity": quantity},
        )
        if not created:
            item.quantity += quantity
            item.save(update_fields=["quantity"])

        return Response(
            {"detail": f"Đã thêm {product.name} vào giỏ.", "quantity": item.quantity},
            status=status.HTTP_200_OK,
        )


class CartRemoveView(APIView):
    permission_classes = (permissions.IsAuthenticated,)

    @extend_schema(
        summary="Xoá sản phẩm khỏi giỏ",
        responses={200: {"type": "object", "properties": {"detail": {"type": "string"}}}},
        tags=["Cart"],
    )
    def delete(self, request: Request, item_id: int) -> Response:
        """Xoá một sản phẩm khỏi giỏ theo item_id."""
        cart = get_or_create_cart(request.user)
        deleted, _ = CartItem.objects.filter(cart=cart, pk=item_id).delete()
        if not deleted:
            return Response({"detail": "Không tìm thấy sản phẩm trong giỏ."}, status=404)
        return Response({"detail": "Đã xoá khỏi giỏ hàng."})


class CartClearView(APIView):
    permission_classes = (permissions.IsAuthenticated,)

    @extend_schema(
        summary="Xoá toàn bộ giỏ hàng",
        responses={200: {"type": "object", "properties": {"detail": {"type": "string"}}}},
        tags=["Cart"],
    )
    def delete(self, request: Request) -> Response:
        """Làm trống toàn bộ giỏ hàng."""
        cart = get_or_create_cart(request.user)
        cart.clear()
        return Response({"detail": "Đã làm trống giỏ hàng."})