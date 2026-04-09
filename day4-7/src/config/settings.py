"""
src/config/settings.py — Cấu hình ứng dụng bằng pydantic-settings.

Đọc từ biến môi trường hoặc file .env.
Prefix: BLOG_
"""
from pydantic import Field
from pydantic_settings import BaseSettings


class DatabaseSettings(BaseSettings):
    """Cấu hình kết nối PostgreSQL (Day 5)."""

    url: str = "postgresql+asyncpg://postgres:postgres@localhost:5432/blog_db"

    model_config = {"env_prefix": "DATABASE_", "env_file": ".env", "extra": "ignore"}


class JWTSettings(BaseSettings):
    """Cấu hình JWT (Day 6)."""

    secret_key: str = "change-me-in-production-use-openssl-rand-hex-32"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    refresh_token_expire_days: int = 7

    model_config = {"env_prefix": "JWT_", "env_file": ".env", "extra": "ignore"}


class Settings(BaseSettings):
    """Cấu hình chính của ứng dụng."""

    app_name: str = "Blog API"
    app_version: str = "1.0.0"
    debug: bool = False
    log_level: str = "INFO"

    # Nested settings
    database: DatabaseSettings = Field(default_factory=DatabaseSettings)
    jwt: JWTSettings = Field(default_factory=JWTSettings)

    model_config = {"env_prefix": "BLOG_", "env_file": ".env", "extra": "ignore"}


settings = Settings()