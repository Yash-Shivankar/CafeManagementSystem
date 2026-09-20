from sqlalchemy import (
    Column,
    DateTime,
    ForeignKey,
    Index,
    Integer,
    Numeric,
    func,
)
from sqlalchemy import (
    Enum as SQLEnum,
)
from sqlalchemy.orm import relationship

from app.models.Common import Common
from app.models.Enums import IncentiveType, enum_values


class Incentives(Common):
    __tablename__ = "incentives"
    __table_args__ = (Index("ix_incentives_outlet_deleted", "outlet_id", "is_deleted"),)

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

    type = Column(
        SQLEnum(IncentiveType, name="incentive_type_enum", values_callable=enum_values),
        nullable=False,
    )

    amount = Column(Numeric(10, 2), nullable=False)

    date_given = Column(DateTime(timezone=True), server_default=func.now())

    employee = relationship(
        "EmployeeDetails",
        foreign_keys=[employee_id],
        back_populates="incentives",
    )

    outlet = relationship("Outlet", foreign_keys=[outlet_id])

    def __repr__(self):
        return f"<Incentive emp={self.employee_id} type={self.type} amount={self.amount}>"
