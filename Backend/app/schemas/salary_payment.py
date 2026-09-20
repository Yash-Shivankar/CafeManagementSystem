from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field

from app.schemas.employee_details import EmployeeDetailsOut


class SalaryPaymentBase(BaseModel):
    employee_id: int = Field(..., json_schema_extra={"example": 101})

    month: str = Field(..., json_schema_extra={"example": "January"})
    year: int = Field(..., ge=2000, le=2100, json_schema_extra={"example": 2025})

    gross_salary: Decimal = Field(..., gt=0, json_schema_extra={"example": 50000})
    net_salary: Decimal = Field(..., gt=0, json_schema_extra={"example": 45000})

    pf_deducted: Decimal = Field(default=Decimal("0"), ge=0, json_schema_extra={"example": 1800})
    esi_deducted: Decimal = Field(default=Decimal("0"), ge=0, json_schema_extra={"example": 375})

    paid_on: datetime | None = None


class SalaryPaymentCreate(SalaryPaymentBase):
    """Schema for creating a salary payment.

    `net_salary` may be omitted — prefer `POST /salary-payments/generate`,
    which computes the whole payslip from the employee's structure and their
    actual attendance, and returns the workings with it.
    """

    net_salary: Decimal = Field(default=Decimal("0"), ge=0)


class SalaryPaymentUpdate(BaseModel):
    """Schema for updating salary payment (partial update allowed)"""

    gross_salary: Decimal | None = Field(None, gt=0)

    pf_deducted: Decimal | None = Field(None, ge=0)
    esi_deducted: Decimal | None = Field(None, ge=0)

    paid_on: datetime | None = None


class SalaryPaymentOut(SalaryPaymentBase):
    id: int
    employee: EmployeeDetailsOut | None
    month: str = Field(..., json_schema_extra={"example": "January"})
    year: int = Field(..., ge=2000, le=2100, json_schema_extra={"example": 2025})
    gross_salary: Decimal = Field(..., gt=0, json_schema_extra={"example": 50000})
    net_salary: Decimal = Field(..., gt=0, json_schema_extra={"example": 45000})
    pf_deducted: Decimal = Field(default=Decimal("0"), ge=0, json_schema_extra={"example": 1800})
    esi_deducted: Decimal = Field(default=Decimal("0"), ge=0, json_schema_extra={"example": 375})
    paid_on: datetime | None = None
    created_at: datetime
    updated_at: datetime
    created_by: int | None = None
    updated_by: int | None = None

    model_config = ConfigDict(from_attributes=True)


class PaginatedSalaryPaymentOut(BaseModel):
    data: list[SalaryPaymentOut]
    total: int
    totalPages: int
    currentPage: int


class PayrollBreakdown(BaseModel):
    """The workings, returned alongside the figures.

    Payroll that cannot be explained to the person being paid is payroll that
    gets argued about.
    """

    monthly_salary: Decimal
    recorded_days: int
    present_days: int
    leave_days: int
    absent_days: int
    payable_days: int
    basic_for_period: Decimal
    allowances: Decimal
    other_deductions: Decimal


class PayrollRequest(BaseModel):
    employee_id: int
    month: str = Field(..., description="Month name, e.g. January or Jan")
    year: int = Field(..., ge=2000, le=2100)


class PayrollPreview(BaseModel):
    employee_id: int
    month: str
    year: int
    gross_salary: Decimal
    net_salary: Decimal
    pf_deducted: Decimal
    esi_deducted: Decimal
    breakdown: PayrollBreakdown
