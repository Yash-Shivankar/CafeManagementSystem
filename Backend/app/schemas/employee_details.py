# app/schemas/employee_details.py
from datetime import date, datetime
from typing import Optional, List
from pydantic import BaseModel
from app.models.Enums import EmploymentType, EmployeeStatus
from app.schemas.user import UserOut
from app.schemas.department import DepartmentOut
from app.schemas.designation import DesignationOut


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
    user: Optional[UserOut]
    employee_code: str
    joining_date: date
    employment_type: EmploymentType
    status: Optional[EmployeeStatus] = EmployeeStatus.ACTIVE
    department: Optional[DepartmentOut]
    designation: Optional[DesignationOut]
    created_at: datetime
    updated_at: datetime
    created_by: Optional[int] = None
    updated_by: Optional[int] = None
    # deleted_at: Optional[datetime] = None
    # is_deleted: Optional[bool] = False

    class Config:
        from_attributes = True


class PaginatedEmployeeDetailsOut(BaseModel):
    data: List[EmployeeDetailsOut]
    total: int
    totalPages: int
    currentPage: int
