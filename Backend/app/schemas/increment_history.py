from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field, model_validator

from app.schemas.employee_details import EmployeeDetailsOut


class IncrementHistoryBase(BaseModel):
    employee_id: int
    old_package: Decimal = Field(gt=0)
    increment_percentage: Decimal = Field(gt=0)

    @model_validator(mode="after")
    def calculate_new_package(self):
        self.new_package = self.old_package + (
            self.old_package * self.increment_percentage / Decimal("100")
        )
        return self


class IncrementHistoryCreate(IncrementHistoryBase):
    pass


class IncrementHistoryUpdate(BaseModel):
    old_package: Decimal | None = Field(default=None, gt=0)
    increment_percentage: Decimal | None = Field(default=None, gt=0)


class IncrementHistoryOut(IncrementHistoryBase):
    id: int
    employee: EmployeeDetailsOut | None
    old_package: Decimal = Field(gt=0)
    new_package: Decimal = Field(gt=0)
    increment_percentage: Decimal = Field(gt=0)
    increment_date: datetime

    created_at: datetime
    updated_at: datetime
    created_by: int | None = None
    updated_by: int | None = None

    model_config = ConfigDict(from_attributes=True)


class PaginatedIncrementHistoryOut(BaseModel):
    data: list[IncrementHistoryOut]
    total: int
    totalPages: int
    currentPage: int
