"""config/celery.py — Cấu hình Celery app. Day 11."""
import os
from celery import Celery

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings.local")

app = Celery("shop_service")
app.config_from_object("django.conf:settings", namespace="CELERY")

# Tự động tìm tasks.py trong tất cả installed apps
app.autodiscover_tasks()