from calendar import monthrange
from datetime import date

from app.models.EmployeeAttendance import EmployeeAttendance
from app.models.Enums import AttendanceStatus
from app.repositories.baseRepository import BaseRepository


class EmployeeAttendanceRepository(BaseRepository[EmployeeAttendance]):
    """Every attendance query lives here."""

    model = EmployeeAttendance
    default_relationships = ("employee",)
    search_relations = (("employee.user", ("first_name", "last_name")),)
    order_by_column = "date"
    filter_map = {
        "start_date": ("date", "gte"),
        "end_date": ("date", "lte"),
        "session": ("session", "eq"),
        "status": ("status", "eq"),
        "employee_id": ("employee_id", "eq"),
    }

    def month_summary(self, employee_id: int, year: int, month: int) -> dict:
        """Distinct days worked, on leave and absent in a calendar month.

        Counted by distinct *date*, not by row: attendance is recorded per
        session, so a full day produces two rows and counting rows would pay
        everyone twice. A day where any session was present counts as present;
        leave only counts where the day was not worked at all.
        """
        first = date(year, month, 1)
        last = date(year, month, monthrange(year, month)[1])

        per_day: dict[date, set] = {}
        detail = (
            self.db.query(EmployeeAttendance.date, EmployeeAttendance.status)
            .filter(
                EmployeeAttendance.employee_id == employee_id,
                EmployeeAttendance.is_deleted.is_(False),
                EmployeeAttendance.date >= first,
                EmployeeAttendance.date <= last,
            )
            .all()
        )
        for day, status in detail:
            per_day.setdefault(day, set()).add(status)

        present = leave = absent = 0
        for statuses in per_day.values():
            if AttendanceStatus.PRESENT in statuses:
                present += 1
            elif AttendanceStatus.LEAVE in statuses:
                leave += 1
            else:
                absent += 1

        return {
            "recorded_days": len(per_day),
            "present_days": present,
            "leave_days": leave,
            "absent_days": absent,
            "period_start": first,
            "period_end": last,
        }
