from sqlalchemy import (
    Column,
    Integer,
    Date,
    DateTime,
    ForeignKey,
    Enum as SQLEnum,
    UniqueConstraint,
    CheckConstraint,
)
from sqlalchemy.orm import relationship
from app.models.Common import Common
from app.models.Enums import AttendanceStatus, AttendanceSession


class EmployeeAttendance(Common):
    __tablename__ = "employee_attendance"
    __table_args__ = (
        UniqueConstraint(
            "employee_id",
            "date",
            "session",
            name="uq_employee_attendance_session",
        ),
        CheckConstraint(
            "check_out IS NULL OR check_out >= check_in",
            name="ck_check_out_after_check_in",
        ),
    )

    id = Column(Integer, primary_key=True, index=True)

    employee_id = Column(
        Integer,
        ForeignKey("employee_details.id"),
        nullable=False,
    )

    date = Column(Date, nullable=False)

    session = Column(
        SQLEnum(AttendanceSession, name="attendance_session_enum"),
        nullable=False,
    )

    check_in = Column(DateTime, nullable=True)
    check_out = Column(DateTime, nullable=True)

    status = Column(
        SQLEnum(AttendanceStatus, name="attendance_status_enum"),
        nullable=False,
        default=AttendanceStatus.PRESENT,
    )

    employee = relationship(
        "EmployeeDetails",
        foreign_keys=[employee_id],
        back_populates="attendance_records",
    )

    def __repr__(self):
        return (
            f"<Attendance emp={self.employee_id} "
            f"date={self.date} session={self.session} status={self.status}>"
        )
