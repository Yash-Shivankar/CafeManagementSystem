# app/schemas/employee_details.py
from datetime import date, datetime
from typing import Optional
from pydantic import BaseModel
from app.models.Enums import EmploymentType, EmployeeStatus


class EmployeeDetailsBase(BaseModel):
    user_id: int
    employee_code: str
    joining_date: date
    employment_type: EmploymentType
    status: Optional[EmployeeStatus] = EmployeeStatus.ACTIVE
    department_id: int
    designation_id: int


class EmployeeDetailsCreate(EmployeeDetailsBase):
    pass


class EmployeeDetailsUpdate(BaseModel):
    joining_date: Optional[date] = None
    employment_type: Optional[EmploymentType] = None
    status: Optional[EmployeeStatus] = None
    department_id: Optional[int] = None
    designation_id: Optional[int] = None
    employee_code: Optional[str] = None


class EmployeeDetailsOut(EmployeeDetailsBase):
    id: int
    created_at: datetime
    updated_at: datetime
    created_by: Optional[int] = None
    updated_by: Optional[int] = None
    deleted_at: Optional[datetime] = None
    is_deleted: Optional[bool] = False

    class Config:
        from_attributes = True
