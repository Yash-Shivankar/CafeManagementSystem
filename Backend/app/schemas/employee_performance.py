from datetime import datetime
from typing import Annotated

from pydantic import BaseModel, ConfigDict, Field

from app.schemas.employee_details import EmployeeDetailsOut


class EmployeePerformanceBase(BaseModel):
    employee_id: int
    rating: Annotated[int, Field(ge=1, le=5)]
    feedback: str | None = None


class EmployeePerformanceCreate(EmployeePerformanceBase):
    pass


class EmployeePerformanceUpdate(BaseModel):
    rating: Annotated[int, Field(ge=1, le=5)] | None = None
    feedback: str | None = None


class EmployeePerformanceOut(BaseModel):
    id: int
    employee: EmployeeDetailsOut | None
    rating: Annotated[int, Field(ge=1, le=5)]
    feedback: str | None = None
    review_date: datetime
    created_at: datetime
    updated_at: datetime
    created_by: int | None = None
    updated_by: int | None = None

    model_config = ConfigDict(from_attributes=True)


class PaginatedEmployeePerformanceOut(BaseModel):
    data: list[EmployeePerformanceOut]
    total: int
    totalPages: int
    currentPage: int
