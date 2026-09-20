import logging
import time
from uuid import uuid4

from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.core.config import settings
from app.dependencies.auth import OUTLET_HEADER
from app.routes import api_router, media_router
from app.utils.exceptions import register_exception_handlers
from app.utils.logging import configure_logging, request_id_var

configure_logging(
    level="DEBUG" if settings.DEBUG else "INFO",
    as_json=settings.is_production,
)

logger = logging.getLogger("caelum")

app = FastAPI(
    title=settings.APP_NAME,
    description="A comprehensive backend for a modern cafe.",
    debug=settings.DEBUG,
    docs_url=None if settings.is_production else "/docs",
    redoc_url=None if settings.is_production else "/redoc",
    openapi_url=None if settings.is_production else "/openapi.json",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"],
    allow_headers=[
        "Authorization",
        "Content-Type",
        "X-Request-ID",
        OUTLET_HEADER,
    ],
    expose_headers=["X-Request-ID"],
    max_age=600,
)


@app.middleware("http")
async def request_context(request: Request, call_next):
    request_id = request.headers.get("x-request-id") or uuid4().hex
    token = request_id_var.set(request_id)
    started = time.perf_counter()

    try:
        response = await call_next(request)
    except Exception:
        logger.exception(
            "Unhandled error",
            extra={"method": request.method, "path": request.url.path},
        )
        raise
    finally:
        request_id_var.reset(token)

    duration_ms = round((time.perf_counter() - started) * 1000, 2)
    response.headers["X-Request-ID"] = request_id
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["Referrer-Policy"] = "no-referrer"

    logger.info(
        "request",
        extra={
            "method": request.method,
            "path": request.url.path,
            "status_code": response.status_code,
            "duration_ms": duration_ms,
        },
    )
    return response


register_exception_handlers(app)


@app.exception_handler(Exception)
async def unhandled_exception_handler(request: Request, exc: Exception):
    """Never leak a stack trace or an ORM error string to a client in
    production — those disclose table names, column names and file paths."""
    logger.exception("Unhandled exception", extra={"path": request.url.path})
    detail = "Internal server error" if settings.is_production else repr(exc)
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"detail": detail, "request_id": request_id_var.get()},
    )


app.include_router(api_router)

app.include_router(media_router)


@app.get("/", tags=["Health"])
def read_root():
    return {"message": "Welcome to the Cafe Management System API"}


@app.get("/health", tags=["Health"])
def health():
    """Liveness probe — no database hit, so it stays green while the DB is
    restarting and the orchestrator does not kill a recoverable pod."""
    return {"status": "ok", "environment": settings.ENVIRONMENT}


@app.get("/health/ready", tags=["Health"])
def readiness():
    """Readiness probe — fails when the database is unreachable, so a bad
    instance is pulled out of the load balancer instead of serving errors."""
    from sqlalchemy import text

    from app.core.database import SessionLocal

    db = SessionLocal()
    try:
        db.execute(text("SELECT 1"))
        return {"status": "ready", "database": "up"}
    except Exception as exc:
        logger.error("Readiness check failed: %s", exc)
        return JSONResponse(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            content={"status": "not-ready", "database": "down"},
        )
    finally:
        db.close()
