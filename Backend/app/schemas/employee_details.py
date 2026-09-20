from datetime import date, datetime

from pydantic import BaseModel, ConfigDict

from app.models.Enums import EmployeeStatus, EmploymentType
from app.schemas.department import DepartmentOut
from app.schemas.designation import DesignationOut
from app.schemas.user import UserOut


class EmployeeDetailsBase(BaseModel):
    user_id: int
    employee_code: str
    joining_date: date
    employment_type: EmploymentType
    status: EmployeeStatus | None = EmployeeStatus.ACTIVE
    department_id: int
    designation_id: int


class EmployeeDetailsCreate(EmployeeDetailsBase):
    pass


class EmployeeDetailsUpdate(BaseModel):
    joining_date: date | None = None
    employment_type: EmploymentType | None = None
    status: EmployeeStatus | None = None
    department_id: int | None = None
    designation_id: int | None = None
    employee_code: str | None = None


class EmployeeDetailsOut(EmployeeDetailsBase):
    id: int
    user: UserOut | None
    employee_code: str
    joining_date: date
    employment_type: EmploymentType
    status: EmployeeStatus | None = EmployeeStatus.ACTIVE
    department: DepartmentOut | None
    designation: DesignationOut | None
    created_at: datetime
    updated_at: datetime
    created_by: int | None = None
    updated_by: int | None = None

    model_config = ConfigDict(from_attributes=True)


class PaginatedEmployeeDetailsOut(BaseModel):
    data: list[EmployeeDetailsOut]
    total: int
    totalPages: int
    currentPage: int
