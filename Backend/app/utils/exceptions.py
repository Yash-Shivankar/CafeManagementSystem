"""Domain errors, and the one place they become HTTP responses.

Services raise these. They know nothing about FastAPI, which is the point: the
same service can be called from a Typer command, a scheduled job or a webhook
handler without dragging `HTTPException` into places that have no HTTP.

`register_exception_handlers(app)` in `app/main.py` does the translation once,
so no controller needs a try/except ladder around every service call.
"""

from __future__ import annotations

from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse

from app.utils.logging import request_id_var


class DomainError(Exception):
    """Base for every expected, caller-fixable failure."""

    status_code: int = status.HTTP_400_BAD_REQUEST
    default_detail: str = "Request could not be completed"

    def __init__(self, detail: str | None = None, *, field: str | None = None):
        self.detail = detail or self.default_detail
        self.field = field
        super().__init__(self.detail)


class NotFoundError(DomainError):
    """a missing row used to surface as a 500.

    `crud.get()` returned None, the route handed None to `response_model`, and
    Pydantic raised on validation — so "department 999 does not exist" read as
    "the server is broken". It is a 404."""

    status_code = status.HTTP_404_NOT_FOUND
    default_detail = "Resource not found"


class ConflictError(DomainError):
    """A uniqueness or state conflict — duplicate email, already-settled
    invoice, double-booked table."""

    status_code = status.HTTP_409_CONFLICT
    default_detail = "Resource already exists"


class ValidationError(DomainError):
    status_code = status.HTTP_422_UNPROCESSABLE_CONTENT
    default_detail = "Invalid data"


class PermissionDeniedError(DomainError):
    status_code = status.HTTP_403_FORBIDDEN
    default_detail = "Not permitted"


class BusinessRuleError(DomainError):
    """An invariant refused the operation — stock would go negative, a payment
    exceeds the invoice balance, attendance is logged twice for one session."""

    status_code = status.HTTP_409_CONFLICT
    default_detail = "Operation violates a business rule"


def register_exception_handlers(app: FastAPI) -> None:
    @app.exception_handler(DomainError)
    async def domain_error_handler(request: Request, exc: DomainError):
        body: dict = {"detail": exc.detail, "request_id": request_id_var.get()}
        if exc.field:
            body["field"] = exc.field
        return JSONResponse(status_code=exc.status_code, content=body)
