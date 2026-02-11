# app/schemas/employee_performance.py
from datetime import datetime
from typing import Optional, Annotated, List
from pydantic import BaseModel, Field
from app.schemas.employee_details import EmployeeDetailsOut


class EmployeePerformanceBase(BaseModel):
    employee_id: int
    rating: Annotated[int, Field(ge=1, le=5)]
    feedback: Optional[str] = None


class EmployeePerformanceCreate(EmployeePerformanceBase):
    pass


class EmployeePerformanceUpdate(BaseModel):
    rating: Optional[Annotated[int, Field(ge=1, le=5)]] = None
    feedback: Optional[str] = None


class EmployeePerformanceOut(BaseModel):
    id: int
    employee: Optional[EmployeeDetailsOut]
    rating: Annotated[int, Field(ge=1, le=5)]
    feedback: Optional[str] = None
    review_date: datetime
    created_at: datetime
    updated_at: datetime
    created_by: Optional[int] = None
    updated_by: Optional[int] = None
    # deleted_at: Optional[datetime] = None
    # is_deleted: Optional[bool] = False

    class Config:
        from_attributes = True


class PaginatedEmployeePerformanceOut(BaseModel):
    data: List[EmployeePerformanceOut]
    total: int
    totalPages: int
    currentPage: int
