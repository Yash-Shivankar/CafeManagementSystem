from datetime import datetime

from pydantic import BaseModel, ConfigDict


class RoleBase(BaseModel):
    role_name: str


class RoleCreate(RoleBase):
    pass


class RoleUpdate(BaseModel):
    role_name: str | None = None


class RoleOut(RoleBase):
    id: int
    created_at: datetime
    updated_at: datetime
    created_by: int | None = None
    updated_by: int | None = None

    model_config = ConfigDict(from_attributes=True)


class PaginatedRoleOut(BaseModel):
    data: list[RoleOut]
    total: int
    totalPages: int
    currentPage: int
