from sqlalchemy import (
    Column,
    Integer,
    Numeric,
    String,
    DateTime,
    ForeignKey,
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
    )

    id = Column(Integer, primary_key=True, index=True)

    employee_id = Column(
        Integer,
        ForeignKey("employee_details.id"),
        nullable=False,
    )

    month = Column(String(20), nullable=False)  # Jan, Feb, March
    year = Column(Integer, nullable=False)

    gross_salary = Column(Numeric(10, 2), nullable=False)
    net_salary = Column(Numeric(10, 2), nullable=False)

    pf_deducted = Column(Numeric(10, 2), default=0)
    esi_deducted = Column(Numeric(10, 2), default=0)

    paid_on = Column(DateTime, server_default=func.now())

    employee = relationship(
        "EmployeeDetails",
        foreign_keys=[employee_id],
        back_populates="salary_payments",
    )

    def __repr__(self):
        return f"<SalaryPayment emp={self.employee_id} {self.month}-{self.year}>"
