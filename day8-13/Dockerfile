FROM python:3.12-slim AS base

WORKDIR /app

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1

FROM base AS builder

RUN pip install --no-cache-dir uv

COPY pyproject.toml ./
RUN uv pip install --system \
    django django-environ djangorestframework djangorestframework-simplejwt \
    django-filter drf-spectacular psycopg[binary] \
    celery redis django-celery-results \
    pillow structlog unidecode \
    pytest pytest-django pytest-cov factory-boy

COPY . .

FROM base AS runtime

COPY --from=builder /usr/local/lib/python3.12/site-packages /usr/local/lib/python3.12/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin
COPY --from=builder /app /app

EXPOSE 8000

CMD ["sh", "-c", "python manage.py migrate && python manage.py collectstatic --noinput && python manage.py runserver 0.0.0.0:8000"]