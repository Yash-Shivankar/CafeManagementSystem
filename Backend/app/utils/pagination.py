"""Pagination, in one place.

Twenty-two route files each carried their own copy of

    skip = (page - 1) * limit
    ...
    total_pages = ceil(total / limit)
    return {"data": rows, "total": total, "totalPages": total_pages,
            "currentPage": page}

which is twenty-two places to fix the `limit == 0` division, twenty-two places
to change the envelope shape, and twenty-two chances for them to drift apart.

The envelope keys stay exactly as they were (`data`, `total`, `totalPages`,
`currentPage`) — the frontend already reads those and this is not the moment to
break it.
"""

from __future__ import annotations

from collections.abc import Sequence
from dataclasses import dataclass
from math import ceil
from typing import Any

from fastapi import Query

DEFAULT_PAGE_SIZE = 10
MAX_PAGE_SIZE = 100


@dataclass(frozen=True)
class PageParams:
    """Injected with `Depends()`, so a route never recomputes `skip` again."""

    page: int = 1
    limit: int = DEFAULT_PAGE_SIZE

    @property
    def skip(self) -> int:
        return (self.page - 1) * self.limit


def page_params(
    page: int = Query(1, ge=1, description="1-based page number"),
    limit: int = Query(DEFAULT_PAGE_SIZE, ge=1, le=MAX_PAGE_SIZE, description="Rows per page"),
) -> PageParams:
    return PageParams(page=page, limit=limit)


def paginate(rows: Sequence[Any], total: int, params: PageParams) -> dict:
    """Wrap a result set in the envelope the SPA expects."""
    limit = max(params.limit, 1)
    return {
        "data": list(rows),
        "total": total,
        "totalPages": ceil(total / limit) if total else 0,
        "currentPage": params.page,
    }
