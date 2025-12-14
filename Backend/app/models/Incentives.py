from sqlalchemy import (
    Column,
    Integer,
    Numeric,
    DateTime,
    ForeignKey,
    Enum as SQLEnum,
    func,
)
from sqlalchemy.orm import relationship
from app.models.Common import Common
from app.models.Enums import IncentiveType


class Incentives(Common):
    __tablename__ = "incentives"

    id = Column(Integer, primary_key=True, index=True)

    employee_id = Column(
        Integer,
        ForeignKey("employee_details.id"),
        nullable=False,
    )

    type = Column(
        SQLEnum(IncentiveType, name="incentive_type_enum"),
        nullable=False,
    )

    amount = Column(Numeric(10, 2), nullable=False)

    date_given = Column(DateTime, server_default=func.now())

    employee = relationship(
        "EmployeeDetails",
        foreign_keys=[employee_id],
        back_populates="incentives",
    )

    def __repr__(self):
        return (
            f"<Incentive emp={self.employee_id} type={self.type} amount={self.amount}>"
        )
