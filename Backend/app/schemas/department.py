# app/schemas/department.py
from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel


class DepartmentBase(BaseModel):
    department_name: str


class DepartmentCreate(DepartmentBase):
    pass  # Only department_name needed for creation


class DepartmentUpdate(BaseModel):
    department_name: Optional[str] = None  # Optional for updates


class DepartmentOut(DepartmentBase):
    id: int
    created_at: datetime
    updated_at: datetime
    created_by: Optional[int] = None
    updated_by: Optional[int] = None
    # deleted_at: Optional[datetime] = None
    # is_deleted: Optional[bool] = False

    class Config:
        from_attributes = True


class PaginatedDepartmentOut(BaseModel):
    data: List[DepartmentOut]
    total: int
    totalPages: int
    currentPage: int
