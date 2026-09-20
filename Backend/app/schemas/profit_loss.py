import datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field


class ProfitLossBase(BaseModel):
    date: datetime.date = Field(..., json_schema_extra={"example": "2025-03-31"})

    revenue: Decimal = Field(..., ge=0, json_schema_extra={"example": 250000.00})
    expenses: Decimal = Field(..., ge=0, json_schema_extra={"example": 180000.00})


class ProfitLossCreate(ProfitLossBase):
    """Schema for creating profit/loss entry"""

    profit: Decimal | None = None


class ProfitLossUpdate(BaseModel):
    """Schema for updating profit/loss (partial updates allowed)"""

    revenue: Decimal | None = Field(None, ge=0)
    expenses: Decimal | None = Field(None, ge=0)
    profit: Decimal | None = Field(None)


class ProfitLossOut(ProfitLossBase):
    id: int
    profit: Decimal | None
    created_at: datetime.datetime
    updated_at: datetime.datetime
    created_by: int | None = None
    updated_by: int | None = None
    deleted_at: datetime.datetime | None = None
    is_deleted: bool

    model_config = ConfigDict(from_attributes=True)


class PaginatedProfitLossOut(BaseModel):
    data: list[ProfitLossOut]
    total: int
    totalPages: int
    currentPage: int


class DayCloseRequest(BaseModel):
    """Revenue is not accepted here — it is read from the payments actually
    recorded for that day, which is the whole point of closing a day."""

    date: datetime.date
    expenses: Decimal = Field(default=Decimal("0"), ge=0)
