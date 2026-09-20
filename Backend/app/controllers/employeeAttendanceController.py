from app.controllers.baseController import BaseController
from app.services.employeeAttendanceService import EmployeeAttendanceService


class EmployeeAttendanceController(BaseController):
    """HTTP shaping for attendance record. No rules — see EmployeeAttendanceService."""

    service_class = EmployeeAttendanceService
