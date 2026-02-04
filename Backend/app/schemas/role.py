# app/schemas/role.py
from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel


class RoleBase(BaseModel):
    role_name: str


class RoleCreate(RoleBase):
    pass  # only role_name needed for creation


class RoleUpdate(BaseModel):
    role_name: Optional[str] = None  # optional for updates


class RoleOut(RoleBase):
    id: int
    created_at: datetime
    updated_at: datetime
    created_by: Optional[int] = None
    updated_by: Optional[int] = None
    # deleted_at: Optional[datetime] = None
    # is_deleted: Optional[bool] = False

    class Config:
        from_attributes = True


class PaginatedRoleOut(BaseModel):
    data: List[RoleOut]
    total: int
    totalPages: int
    currentPage: int
