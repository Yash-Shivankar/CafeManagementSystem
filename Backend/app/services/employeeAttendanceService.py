from app.models.EmployeeAttendance import EmployeeAttendance
from app.repositories.employeeAttendanceRepository import EmployeeAttendanceRepository
from app.services.baseService import BaseService


class EmployeeAttendanceService(BaseService[EmployeeAttendance]):
    """Attendance record use-cases.

    Plain CRUD today. Rules belong here, not in the route: override
    `before_create` / `before_update` / `before_delete` when attendance record
    gains an invariant.
    """

    repository_class = EmployeeAttendanceRepository
    entity_name = "Attendance record"
