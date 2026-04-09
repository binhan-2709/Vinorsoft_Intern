"""
src/api/app.py — FastAPI app factory.

Day 6: Middleware ghi log, xử lý lỗi toàn cục.
Day 7: Lifespan để init/teardown DB connection pool.
"""
import time
from contextlib import asynccontextmanager

import structlog
from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from src.api.v1.auth import router as auth_router
from src.api.v1.posts import router as posts_router
from src.config.settings import settings
from src.db.session import engine

structlog.configure(
    processors=[
        structlog.processors.add_log_level,
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.dev.ConsoleRenderer(),
    ],
    wrapper_class=structlog.make_filtering_bound_logger(20),
    cache_logger_on_first_use=True,
)

logger = structlog.get_logger()


# ── Lifespan (Day 7) ──────────────────────────────────────────────────
@asynccontextmanager
async def lifespan(app: FastAPI):
    """Khởi động và tắt connection pool."""
    logger.info("app_starting", name=settings.app_name, version=settings.app_version)
    yield
    await engine.dispose()
    logger.info("app_stopped")


def create_app() -> FastAPI:
    app = FastAPI(
        title=f"📝 {settings.app_name}",
        version=settings.app_version,
        description="""
## Blog API — FastAPI Day 4 → 7

| Ngày | Kỹ năng |
|------|---------|
| **Day 4** | Pydantic, Path/Query Params, Headers, Cookies |
| **Day 5** | PostgreSQL async, SQLAlchemy, Alembic migrations |
| **Day 6** | JWT Auth, Middleware, OAuth2, Role-based access |
| **Day 7** | Background Tasks, Docker, docker-compose |

### Cách dùng
1. `POST /auth/register` — tạo tài khoản
2. `POST /auth/login` — nhận JWT token
3. Dùng token trong header: `Authorization: Bearer <token>`
""",
        lifespan=lifespan,
    )

    # ── CORS Middleware ───────────────────────────────────────────────
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # ── Logging Middleware (Day 6) ────────────────────────────────────
    @app.middleware("http")
    async def log_requests(request: Request, call_next):
        """Ghi log mỗi request: method, path, status, thời gian xử lý."""
        start = time.perf_counter()
        response = await call_next(request)
        duration_ms = (time.perf_counter() - start) * 1000
        logger.info(
            "http_request",
            method=request.method,
            path=request.url.path,
            status=response.status_code,
            duration_ms=round(duration_ms, 2),
        )
        return response

    # ── Global exception handler ──────────────────────────────────────
    @app.exception_handler(Exception)
    async def global_exception_handler(request: Request, exc: Exception):
        logger.error("unhandled_exception", path=request.url.path, error=str(exc))
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={"detail": "Lỗi server nội bộ."},
        )

    # ── Health check ──────────────────────────────────────────────────
    @app.get("/health", tags=["Health"])
    async def health():
        return {"status": "ok", "service": "blog-api", "version": settings.app_version}

    # ── Routers ───────────────────────────────────────────────────────
    app.include_router(auth_router, prefix="/api/v1")
    app.include_router(posts_router, prefix="/api/v1")


    return app

