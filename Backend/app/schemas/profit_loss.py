import datetime
from typing import Optional, List
from decimal import Decimal

from pydantic import BaseModel, Field, field_validator


class ProfitLossBase(BaseModel):
    date: datetime.date = Field(..., example="2025-03-31")

    revenue: Decimal = Field(..., ge=0, example=250000.00)
    expenses: Decimal = Field(..., ge=0, example=180000.00)
    profit: Decimal = Field(..., example=70000.00)


class ProfitLossCreate(ProfitLossBase):
    """Schema for creating profit/loss entry"""

    pass


class ProfitLossUpdate(BaseModel):
    """Schema for updating profit/loss (partial updates allowed)"""

    revenue: Optional[Decimal] = Field(None, ge=0)
    expenses: Optional[Decimal] = Field(None, ge=0)
    profit: Optional[Decimal] = Field(None)


class ProfitLossOut(ProfitLossBase):
    id: int

    created_at: datetime.datetime
    updated_at: datetime.datetime
    created_by: Optional[int] = None
    updated_by: Optional[int] = None
    deleted_at: Optional[datetime.datetime] = None
    is_deleted: bool

    class Config:
        from_attributes = True


class PaginatedProfitLossOut(BaseModel):
    data: List[ProfitLossOut]
    total: int
    totalPages: int
    currentPage: int
