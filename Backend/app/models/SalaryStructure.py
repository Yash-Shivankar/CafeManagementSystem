from sqlalchemy import (
    Column,
    ForeignKey,
    Index,
    Integer,
    Numeric,
    UniqueConstraint,
)
from sqlalchemy.orm import relationship

from app.models.Common import Common


class SalaryStructure(Common):
    __tablename__ = "salary_structures"
    __table_args__ = (
        UniqueConstraint("employee_id", name="uq_employee_salary_structure"),
        Index("ix_salary_structures_is_deleted", "is_deleted"),
    )

    id = Column(Integer, primary_key=True, index=True)

    employee_id = Column(
        Integer,
        ForeignKey("employee_details.id"),
        nullable=False,
    )

    package_lpa = Column(Numeric(10, 2), nullable=False)
    monthly_salary = Column(Numeric(10, 2), nullable=False)

    pf_percentage = Column(Numeric(5, 2), nullable=False)
    esi_percentage = Column(Numeric(5, 2), nullable=False)

    allowances = Column(Numeric(10, 2), default=0)
    deductions = Column(Numeric(10, 2), default=0)

    employee = relationship(
        "EmployeeDetails",
        foreign_keys=[employee_id],
        back_populates="salary_structure",
    )

    def __repr__(self):
        return f"<SalaryStructure emp={self.employee_id} package={self.package_lpa}>"
