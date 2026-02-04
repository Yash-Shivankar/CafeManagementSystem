from datetime import datetime
from typing import Optional, List
from decimal import Decimal

from pydantic import BaseModel, Field


class SalaryStructureBase(BaseModel):
    employee_id: int = Field(..., example=101)

    package_lpa: Decimal = Field(..., gt=0, example=12.50)
    monthly_salary: Decimal = Field(..., gt=0, example=104166.67)

    pf_percentage: Decimal = Field(..., ge=0, le=100, example=12.00)
    esi_percentage: Decimal = Field(..., ge=0, le=100, example=0.75)

    allowances: Decimal = Field(default=0, ge=0, example=5000)
    deductions: Decimal = Field(default=0, ge=0, example=2000)


class SalaryStructureCreate(SalaryStructureBase):
    """Schema for creating salary structure"""

    pass


class SalaryStructureUpdate(BaseModel):
    """Schema for updating salary structure (partial updates allowed)"""

    package_lpa: Optional[Decimal] = Field(None, gt=0)
    monthly_salary: Optional[Decimal] = Field(None, gt=0)

    pf_percentage: Optional[Decimal] = Field(None, ge=0, le=100)
    esi_percentage: Optional[Decimal] = Field(None, ge=0, le=100)

    allowances: Optional[Decimal] = Field(None, ge=0)
    deductions: Optional[Decimal] = Field(None, ge=0)


class SalaryStructureOut(SalaryStructureBase):
    id: int

    created_at: datetime
    updated_at: datetime
    created_by: Optional[int] = None
    updated_by: Optional[int] = None
    deleted_at: Optional[datetime] = None
    is_deleted: Optional[bool] = False

    class Config:
        from_attributes = True


class PaginatedSalaryStructureOut(BaseModel):
    data: List[SalaryStructureOut]
    total: int
    totalPages: int
    currentPage: int
