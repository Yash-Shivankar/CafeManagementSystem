from datetime import datetime
from typing import Optional, List
from decimal import Decimal

from pydantic import BaseModel, Field


class IncrementHistoryBase(BaseModel):
    employee_id: int
    old_package: Decimal = Field(gt=0)
    new_package: Decimal = Field(gt=0)
    increment_percentage: Decimal = Field(gt=0)


class IncrementHistoryCreate(IncrementHistoryBase):
    pass


class IncrementHistoryUpdate(BaseModel):
    old_package: Optional[Decimal] = Field(default=None, gt=0)
    new_package: Optional[Decimal] = Field(default=None, gt=0)
    increment_percentage: Optional[Decimal] = Field(default=None, gt=0)


class IncrementHistoryOut(IncrementHistoryBase):
    id: int
    increment_date: datetime

    created_at: datetime
    updated_at: datetime
    created_by: Optional[int] = None
    updated_by: Optional[int] = None
    # deleted_at: Optional[datetime] = None
    # is_deleted: Optional[bool] = False

    class Config:
        from_attributes = True


class PaginatedIncrementHistoryOut(BaseModel):
    data: List[IncrementHistoryOut]
    total: int
    totalPages: int
    currentPage: int
