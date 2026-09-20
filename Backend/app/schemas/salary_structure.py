from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field

from app.schemas.employee_details import EmployeeDetailsOut


class SalaryStructureBase(BaseModel):
    employee_id: int = Field(..., json_schema_extra={"example": 101})

    package_lpa: Decimal = Field(..., gt=0, json_schema_extra={"example": 12.50})
    monthly_salary: Decimal = Field(..., gt=0, json_schema_extra={"example": 104166.67})

    pf_percentage: Decimal = Field(..., ge=0, le=100, json_schema_extra={"example": 12.00})
    esi_percentage: Decimal = Field(..., ge=0, le=100, json_schema_extra={"example": 0.75})

    allowances: Decimal = Field(default=Decimal("0"), ge=0, json_schema_extra={"example": 5000})
    deductions: Decimal = Field(default=Decimal("0"), ge=0, json_schema_extra={"example": 2000})


class SalaryStructureCreate(SalaryStructureBase):
    """Schema for creating salary structure"""

    pass


class SalaryStructureUpdate(BaseModel):
    """Schema for updating salary structure (partial updates allowed)"""

    package_lpa: Decimal | None = Field(None, gt=0)
    monthly_salary: Decimal | None = Field(None, gt=0)

    pf_percentage: Decimal | None = Field(None, ge=0, le=100)
    esi_percentage: Decimal | None = Field(None, ge=0, le=100)

    allowances: Decimal | None = Field(None, ge=0)
    deductions: Decimal | None = Field(None, ge=0)


class SalaryStructureOut(SalaryStructureBase):
    id: int
    employee: EmployeeDetailsOut | None
    created_at: datetime
    updated_at: datetime
    created_by: int | None = None
    updated_by: int | None = None
    deleted_at: datetime | None = None
    is_deleted: bool | None = False

    model_config = ConfigDict(from_attributes=True)


class PaginatedSalaryStructureOut(BaseModel):
    data: list[SalaryStructureOut]
    total: int
    totalPages: int
    currentPage: int
