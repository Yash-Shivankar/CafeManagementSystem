"""Audit trail endpoints.

Read-only, by design: an entry exists because something happened, and a record
of what happened that someone can rewrite is not a record of what happened.
"""

from datetime import date

from fastapi import APIRouter, Depends, Query

from app.controllers.auditLogController import AuditLogController
from app.schemas.audit import AuditLogOut, PaginatedAuditLogOut
from app.utils.pagination import PageParams, page_params

router = APIRouter(prefix="/audit-logs", tags=["Activity Log"])


@router.get("/", response_model=PaginatedAuditLogOut)
def list_audit_logs(
    table_name: str | None = Query(None),
    record_id: int | None = Query(None),
    action: str | None = Query(None, pattern="^(create|update|delete)$"),
    actor_id: int | None = Query(None),
    start_date: date | None = Query(None),
    end_date: date | None = Query(None),
    search: str | None = Query(None, min_length=1),
    params: PageParams = Depends(page_params),
    controller: AuditLogController = Depends(),
):
    return controller.list(
        params,
        search=search,
        table_name=table_name,
        record_id=record_id,
        action=action,
        actor_id=actor_id,
        start_date=start_date,
        end_date=end_date,
    )


@router.get("/{table_name}/{record_id}", response_model=list[AuditLogOut])
def record_history(
    table_name: str,
    record_id: int,
    controller: AuditLogController = Depends(),
):
    """Everything that ever happened to one row — the "why is this number
    different from last week" question, answered."""
    return controller.history_for(table_name, record_id)
