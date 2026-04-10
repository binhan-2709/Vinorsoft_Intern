"""
apps/orders/tasks.py — Celery tasks.

Day 11: Tác vụ bất đồng bộ chạy trong Celery worker (Redis broker).
        Không block HTTP request — người dùng nhận response ngay lập tức.
"""
import structlog
from celery import shared_task
from django.core.mail import send_mail
from django.conf import settings

logger = structlog.get_logger()


@shared_task(bind=True, max_retries=3, default_retry_delay=60)
def send_order_confirmation_email(self, order_id: int) -> str:
    """
    Task: Gửi email xác nhận đơn hàng.

    Day 11: bind=True để có thể retry khi lỗi.
    Celery worker chạy task này ở background — không ảnh hưởng response.
    """
    try:
        from .models import Order
        order = Order.objects.select_related("user").prefetch_related("items__product").get(pk=order_id)

        subject = f"[Shop] Xác nhận đơn hàng #{order.pk}"
        message = f"""
Xin chào {order.user.username},

Đơn hàng #{order.pk} của bạn đã được đặt thành công!

Chi tiết:
{chr(10).join(f"  - {item.product.name} x{item.quantity}: {item.subtotal:,.0f}đ" for item in order.items.all())}

Tổng tiền: {order.total_price:,.0f}đ
Địa chỉ giao: {order.shipping_address}

Cảm ơn bạn đã mua hàng!
"""
        send_mail(
            subject=subject,
            message=message,
            from_email=getattr(settings, "DEFAULT_FROM_EMAIL", "noreply@shop.com"),
            recipient_list=[order.user.email],
            fail_silently=False,
        )
        logger.info("email_sent", order_id=order_id, email=order.user.email)
        return f"Email gửi thành công cho đơn #{order_id}"

    except Exception as exc:
        logger.error("email_failed", order_id=order_id, error=str(exc))
        raise self.retry(exc=exc)


@shared_task
def restore_stock_on_cancel(order_id: int) -> str:
    """
    Task: Hoàn lại tồn kho khi đơn hàng bị huỷ.

    Day 11: Chạy async để không block request huỷ đơn.
    """
    from .models import OrderItem
    from apps.inventory.models import Product

    items = OrderItem.objects.filter(order_id=order_id).select_related("product")
    for item in items:
        Product.objects.filter(pk=item.product_id).update(
            stock=item.product.stock + item.quantity
        )
        logger.info("stock_restored", product_id=item.product_id, qty=item.quantity)

    return f"Đã hoàn kho cho đơn #{order_id}"