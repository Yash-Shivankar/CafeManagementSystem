# app/schemas/employee_attendance.py
from datetime import date, datetime
from typing import Optional
from pydantic import BaseModel
from app.models.Enums import AttendanceStatus, AttendanceSession


class EmployeeAttendanceBase(BaseModel):
    employee_id: int
    date: date
    session: AttendanceSession
    check_in: Optional[datetime] = None
    check_out: Optional[datetime] = None
    status: Optional[AttendanceStatus] = AttendanceStatus.PRESENT


class EmployeeAttendanceCreate(EmployeeAttendanceBase):
    pass


class EmployeeAttendanceUpdate(BaseModel):
    check_in: Optional[datetime] = None
    check_out: Optional[datetime] = None
    status: Optional[AttendanceStatus] = None


class EmployeeAttendanceOut(EmployeeAttendanceBase):
    id: int
    created_at: datetime
    updated_at: datetime
    created_by: Optional[int] = None
    updated_by: Optional[int] = None
    deleted_at: Optional[datetime] = None
    is_deleted: Optional[bool] = False

    class Config:
        from_attributes = True
