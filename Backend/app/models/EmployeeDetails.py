from sqlalchemy import (
    Column,
    Date,
    ForeignKey,
    Index,
    Integer,
    String,
    UniqueConstraint,
)
from sqlalchemy import (
    Enum as SQLEnum,
)
from sqlalchemy.orm import relationship

from app.models.Common import Common
from app.models.Enums import EmployeeStatus, EmploymentType, enum_values  # noqa: F403


class EmployeeDetails(Common):
    __tablename__ = "employee_details"
    __table_args__ = (
        UniqueConstraint("employee_code", name="uq_employee_code"),
        Index("ix_employee_details_outlet_deleted", "outlet_id", "is_deleted"),
    )

    id = Column(Integer, primary_key=True, index=True)
    outlet_id = Column(
        Integer,
        ForeignKey("outlets.id"),
        nullable=True,
        index=True,
    )
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    employee_code = Column(String(255), nullable=False)
    joining_date = Column(Date, nullable=False)
    employment_type = Column(
        SQLEnum(EmploymentType, name="employment_type_enum", values_callable=enum_values),
        nullable=False,
    )
    status = Column(
        SQLEnum(EmployeeStatus, name="employee_status_enum", values_callable=enum_values),
        nullable=False,
        default=EmployeeStatus.ACTIVE,
    )
    department_id = Column(Integer, ForeignKey("departments.id"), nullable=False)
    designation_id = Column(Integer, ForeignKey("designations.id"), nullable=False)

    user = relationship(
        "User",
        foreign_keys=[user_id],
        back_populates="employee_details",
    )

    department = relationship(
        "Department",
        foreign_keys=[department_id],
        back_populates="employees",
    )

    designation = relationship(
        "Designation",
        foreign_keys=[designation_id],
        back_populates="employees",
    )

    attendance_records = relationship(
        "EmployeeAttendance",
        foreign_keys="EmployeeAttendance.employee_id",
        back_populates="employee",
        cascade="all, delete-orphan",
    )

    documents = relationship(
        "EmployeeDocument",
        foreign_keys="EmployeeDocument.employee_id",
        back_populates="employee",
        cascade="all, delete-orphan",
    )

    performance_reviews = relationship(
        "EmployeePerformance",
        foreign_keys="EmployeePerformance.employee_id",
        back_populates="employee",
        cascade="all, delete-orphan",
    )

    salary_structure = relationship(
        "SalaryStructure",
        foreign_keys="SalaryStructure.employee_id",
        back_populates="employee",
        uselist=False,
    )

    salary_payments = relationship(
        "SalaryPayment",
        foreign_keys="SalaryPayment.employee_id",
        back_populates="employee",
    )

    incentives = relationship(
        "Incentives",
        foreign_keys="Incentives.employee_id",
        back_populates="employee",
    )

    increment_history = relationship(
        "IncrementHistory",
        foreign_keys="IncrementHistory.employee_id",
        back_populates="employee",
    )

    outlet = relationship("Outlet", foreign_keys=[outlet_id])

    def __repr__(self):
        return f"<EmployeeDetails id={self.id} code={self.employee_code}>"
