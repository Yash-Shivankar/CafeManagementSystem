from datetime import datetime
from typing import Optional
from decimal import Decimal

from pydantic import BaseModel, Field, field_validator


class SalaryPaymentBase(BaseModel):
    employee_id: int = Field(..., example=101)

    month: str = Field(..., example="January")
    year: int = Field(..., ge=2000, le=2100, example=2025)

    gross_salary: Decimal = Field(..., gt=0, example=50000)
    net_salary: Decimal = Field(..., gt=0, example=45000)

    pf_deducted: Decimal = Field(default=0, ge=0, example=1800)
    esi_deducted: Decimal = Field(default=0, ge=0, example=375)

    paid_on: Optional[datetime] = None


class SalaryPaymentCreate(SalaryPaymentBase):
    """Schema for creating salary payment"""

    pass


class SalaryPaymentUpdate(BaseModel):
    """Schema for updating salary payment (partial update allowed)"""

    gross_salary: Optional[Decimal] = Field(None, gt=0)
    net_salary: Optional[Decimal] = Field(None, gt=0)

    pf_deducted: Optional[Decimal] = Field(None, ge=0)
    esi_deducted: Optional[Decimal] = Field(None, ge=0)

    paid_on: Optional[datetime] = None


class SalaryPaymentOut(SalaryPaymentBase):
    id: int

    created_at: datetime
    updated_at: datetime
    created_by: Optional[int] = None
    updated_by: Optional[int] = None
    deleted_at: Optional[datetime] = None
    is_deleted: bool

    class Config:
        from_attributes = True
