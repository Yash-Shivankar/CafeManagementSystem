from datetime import date, datetime

from pydantic import BaseModel, ConfigDict

from app.models.Enums import AttendanceSession, AttendanceStatus
from app.schemas.employee_details import EmployeeDetailsOut


class EmployeeAttendanceBase(BaseModel):
    employee_id: int
    date: date
    session: AttendanceSession
    check_in: datetime | None = None
    check_out: datetime | None = None
    status: AttendanceStatus | None = AttendanceStatus.PRESENT


class EmployeeAttendanceCreate(EmployeeAttendanceBase):
    pass


class EmployeeAttendanceUpdate(BaseModel):
    check_in: datetime | None = None
    check_out: datetime | None = None
    status: AttendanceStatus | None = None


class EmployeeAttendanceOut(BaseModel):
    id: int
    employee: EmployeeDetailsOut | None = {}
    date: date
    session: AttendanceSession
    check_in: datetime | None = None
    check_out: datetime | None = None
    status: AttendanceStatus | None = AttendanceStatus.PRESENT
    created_at: datetime
    updated_at: datetime
    created_by: int | None = None
    updated_by: int | None = None

    model_config = ConfigDict(from_attributes=True)


class PaginatedEmployeeAttendanceOut(BaseModel):
    data: list[EmployeeAttendanceOut]
    total: int
    totalPages: int
    currentPage: int
