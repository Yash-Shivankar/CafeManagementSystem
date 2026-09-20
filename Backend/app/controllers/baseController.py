"""The generic controller.

Injected per request, already holding the session, the current user and a
service built from both. Route handlers shrink to a signature and one call.

There is no try/except here on purpose: services raise `DomainError`
subclasses, and `register_exception_handlers` in `app/main.py` turns each of
them into the right status code once, centrally. A ladder of try/except in
every handler is exactly the duplication this refactor is removing.
"""

from __future__ import annotations

from collections.abc import Sequence
from typing import Any

from fastapi import Depends, Request
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.dependencies.auth import client_ip, get_current_outlet, get_current_user
from app.models.User import User
from app.services.baseService import BaseService
from app.utils.pagination import PageParams, page_params, paginate


class BaseController:
    service_class: type[BaseService]

    def __init__(
        self,
        request: Request,
        db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user),
        outlet_id: int | None = Depends(get_current_outlet),
    ):
        self.db = db
        self.current_user = current_user
        self.outlet_id = outlet_id
        self.service: BaseService = self.service_class(
            db,
            actor=current_user,
            outlet_id=outlet_id,
            ip_address=client_ip(request),
        )

    def list(
        self,
        params: PageParams,
        search: str | None = None,
        relationships: Sequence[str] | None = None,
        **filter_values: Any,
    ) -> dict:
        """Route handlers pass their query parameters straight through as
        keyword arguments; the repository's `filter_map` interprets them."""
        rows, total = self.service.list(
            params,
            filter_values=filter_values,
            search=search,
            relationships=relationships,
        )
        return paginate(rows, total, params)

    def get(self, id: int) -> Any:
        return self.service.get(id)

    def create(self, payload) -> Any:
        return self.service.create(payload)

    def update(self, id: int, payload) -> Any:
        return self.service.update(id, payload)

    def delete(self, id: int) -> Any:
        return self.service.delete(id)


Page = Depends(page_params)

__all__ = ["BaseController", "Page", "PageParams", "page_params"]
