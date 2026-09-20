from sqlalchemy import (
    Column,
    DateTime,
    ForeignKey,
    Index,
    Integer,
    Numeric,
    String,
    UniqueConstraint,
    func,
)
from sqlalchemy.orm import relationship

from app.models.Common import Common


class SalaryPayment(Common):
    __tablename__ = "salary_payments"
    __table_args__ = (
        UniqueConstraint(
            "employee_id",
            "month",
            "year",
            name="uq_employee_salary_month",
        ),
        Index("ix_salary_payments_outlet_deleted", "outlet_id", "is_deleted"),
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

    month = Column(String(20), nullable=False)
    year = Column(Integer, nullable=False)

    gross_salary = Column(Numeric(10, 2), nullable=False)
    net_salary = Column(Numeric(10, 2), nullable=False)

    pf_deducted = Column(Numeric(10, 2), default=0)
    esi_deducted = Column(Numeric(10, 2), default=0)

    paid_on = Column(DateTime(timezone=True), server_default=func.now())

    employee = relationship(
        "EmployeeDetails",
        foreign_keys=[employee_id],
        back_populates="salary_payments",
    )

    outlet = relationship("Outlet", foreign_keys=[outlet_id])

    def __repr__(self):
        return f"<SalaryPayment emp={self.employee_id} {self.month}-{self.year}>"
