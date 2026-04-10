#!/usr/bin/env python
"""Django manage.py entry point."""
import os
import sys


def main() -> None:
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings.local")
    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError("Không tìm thấy Django. Hãy chạy: pip install django") from exc
    execute_from_command_line(sys.argv)


if __name__ == "__main__":
    main()