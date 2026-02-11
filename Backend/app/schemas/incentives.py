from datetime import datetime
from typing import Optional, List
from decimal import Decimal

from pydantic import BaseModel, Field
from app.models.Enums import IncentiveType
from app.schemas.employee_details import EmployeeDetailsOut


class IncentiveBase(BaseModel):
    employee_id: int
    type: IncentiveType
    amount: Decimal = Field(gt=0)


class IncentiveCreate(IncentiveBase):
    pass


class IncentiveUpdate(BaseModel):
    type: Optional[IncentiveType] = None
    amount: Optional[Decimal] = Field(default=None, gt=0)


class IncentiveOut(IncentiveBase):
    id: int
    employee: Optional[EmployeeDetailsOut]
    type: IncentiveType
    amount: Decimal = Field(gt=0)
    date_given: datetime
    created_at: datetime
    updated_at: datetime
    created_by: Optional[int] = None
    updated_by: Optional[int] = None
    # deleted_at: Optional[datetime] = None
    # is_deleted: Optional[bool] = False

    class Config:
        from_attributes = True


class PaginatedIncentiveOut(BaseModel):
    data: List[IncentiveOut]
    total: int
    totalPages: int
    currentPage: int
