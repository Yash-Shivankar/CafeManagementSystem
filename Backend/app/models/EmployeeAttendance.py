from sqlalchemy import (
    CheckConstraint,
    Column,
    Date,
    DateTime,
    ForeignKey,
    Index,
    Integer,
    UniqueConstraint,
)
from sqlalchemy import (
    Enum as SQLEnum,
)
from sqlalchemy.orm import relationship

from app.models.Common import Common
from app.models.Enums import AttendanceSession, AttendanceStatus, enum_values


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
        Index("ix_employee_attendance_outlet_deleted", "outlet_id", "is_deleted"),
    )

    id = Column(Integer, primary_key=True, index=True)
    outlet_id = Column(
        Integer,
        ForeignKey("outlets.id"),
        nullable=False,
        index=True,
    )

    employee_id = Column(
        Integer,
        ForeignKey("employee_details.id"),
        nullable=False,
    )

    date = Column(Date, nullable=False)

    session = Column(
        SQLEnum(AttendanceSession, name="attendance_session_enum", values_callable=enum_values),
        nullable=False,
    )

    check_in = Column(DateTime(timezone=True), nullable=True)
    check_out = Column(DateTime(timezone=True), nullable=True)

    status = Column(
        SQLEnum(AttendanceStatus, name="attendance_status_enum", values_callable=enum_values),
        nullable=False,
        default=AttendanceStatus.PRESENT,
    )

    employee = relationship(
        "EmployeeDetails",
        foreign_keys=[employee_id],
        back_populates="attendance_records",
    )

    outlet = relationship("Outlet", foreign_keys=[outlet_id])

    def __repr__(self):
        return (
            f"<Attendance emp={self.employee_id} "
            f"date={self.date} session={self.session} status={self.status}>"
        )
