from datetime import datetime

from pydantic import BaseModel, EmailStr


class SessionUser(BaseModel):
    id: int
    first_name: str | None = None
    last_name: str | None = None
    email: EmailStr | None = None

    model_config = {"from_attributes": True}


class SessionOut(BaseModel):
    id: int
    user: SessionUser | None = None
    ip_address: str | None = None
    user_agent: str | None = None
    created_at: datetime
    expires_at: datetime
    revoked_at: datetime | None = None

    model_config = {"from_attributes": True}


class PaginatedSessionOut(BaseModel):
    data: list[SessionOut]
    total: int
    totalPages: int
    currentPage: int
