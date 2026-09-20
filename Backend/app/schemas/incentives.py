from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field

from app.models.Enums import IncentiveType
from app.schemas.employee_details import EmployeeDetailsOut


class IncentiveBase(BaseModel):
    employee_id: int
    type: IncentiveType
    amount: Decimal = Field(gt=0)


class IncentiveCreate(IncentiveBase):
    pass


class IncentiveUpdate(BaseModel):
    type: IncentiveType | None = None
    amount: Decimal | None = Field(default=None, gt=0)


class IncentiveOut(IncentiveBase):
    id: int
    employee: EmployeeDetailsOut | None
    type: IncentiveType
    amount: Decimal = Field(gt=0)
    date_given: datetime
    created_at: datetime
    updated_at: datetime
    created_by: int | None = None
    updated_by: int | None = None

    model_config = ConfigDict(from_attributes=True)


class PaginatedIncentiveOut(BaseModel):
    data: list[IncentiveOut]
    total: int
    totalPages: int
    currentPage: int
