from datetime import datetime
from typing import Any

from pydantic import BaseModel, EmailStr


class AuditActor(BaseModel):
    id: int
    first_name: str | None = None
    last_name: str | None = None
    email: EmailStr | None = None

    model_config = {"from_attributes": True}


class AuditLogOut(BaseModel):
    id: int
    table_name: str
    record_id: int | None = None
    action: str
    changes: dict[str, Any] | None = None
    actor: AuditActor | None = None
    actor_role: str | None = None
    ip_address: str | None = None
    created_at: datetime

    model_config = {"from_attributes": True}


class PaginatedAuditLogOut(BaseModel):
    data: list[AuditLogOut]
    total: int
    totalPages: int
    currentPage: int
