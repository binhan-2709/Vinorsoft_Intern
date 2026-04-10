"""
apps/orders/signals.py — Django Signals.

Day 11: post_save signal tự động trigger khi Order được tạo mới,
        gọi Celery task gửi email thông báo (không block request).
"""
import structlog
from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver

from .models import Order

logger = structlog.get_logger()


@receiver(post_save, sender=Order)
def on_order_created(sender, instance: Order, created: bool, **kwargs) -> None:
    """
    Signal: sau khi Order được tạo mới.

    Day 11: Import task ở đây (tránh circular import),
            delay() để gửi sang Celery worker.
    """
    if created:
        logger.info("order_created", order_id=instance.pk, user=instance.user.email)

        # Gọi Celery task bất đồng bộ — không block response
        from .tasks import send_order_confirmation_email
        send_order_confirmation_email.delay(instance.pk)


@receiver(pre_save, sender=Order)
def on_order_status_changed(sender, instance: Order, **kwargs) -> None:
    """
    Signal: trước khi lưu — kiểm tra status thay đổi.
    """
    if instance.pk:
        try:
            old = Order.objects.get(pk=instance.pk)
            if old.status != instance.status:
                logger.info(
                    "order_status_changed",
                    order_id=instance.pk,
                    old=old.status,
                    new=instance.status,
                )
                # Nếu huỷ đơn → hoàn lại tồn kho
                if instance.status == Order.Status.CANCELLED:
                    from .tasks import restore_stock_on_cancel
                    restore_stock_on_cancel.delay(instance.pk)
        except Order.DoesNotExist:
            pass