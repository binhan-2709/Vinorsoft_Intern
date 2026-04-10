"""config/settings/local.py — Dev môi trường."""
from .base import *  # noqa: F401, F403

DEBUG = True
ALLOWED_HOSTS = ["*"]

# Hiện SQL queries khi debug
LOGGING = {
    "version": 1,
    "handlers": {"console": {"class": "logging.StreamHandler"}},
    "loggers": {"django.db.backends": {"level": "DEBUG", "handlers": ["console"]}},
}