"""Use-cases. Everything that decides *what happens* lives here.

A service knows about repositories, models, domain errors and other services.
It knows nothing about FastAPI — no `Request`, no `HTTPException`, no
`response_model` — so the same use-case can be driven from the API, from a
Typer command in `app/commands/`, or from a future scheduled job without
dragging HTTP into places that have none.

A service owns the transaction: it calls `commit()` at the end of a use-case,
and repositories only `flush()`. That is what makes a multi-write operation
all-or-nothing.
"""

from app.services.baseService import BaseService

__all__ = ["BaseService"]
