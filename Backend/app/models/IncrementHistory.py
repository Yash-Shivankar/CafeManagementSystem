from sqlalchemy import (
    Column,
    Integer,
    Numeric,
    DateTime,
    ForeignKey,
    func,
)
from sqlalchemy.orm import relationship
from app.models.Common import Common


class IncrementHistory(Common):
    __tablename__ = "increment_history"

    id = Column(Integer, primary_key=True, index=True)

    employee_id = Column(
        Integer,
        ForeignKey("employee_details.id"),
        nullable=False,
    )

    old_package = Column(Numeric(10, 2), nullable=False)
    new_package = Column(Numeric(10, 2), nullable=False)
    increment_percentage = Column(
        Numeric(5, 2),
        nullable=False,
    )

    increment_date = Column(DateTime, server_default=func.now())

    employee = relationship(
        "EmployeeDetails",
        foreign_keys=[employee_id],
        back_populates="increment_history",
    )

    def __repr__(self):
        return f"<Increment emp={self.employee_id} {self.old_package}->{self.new_package} ({self.increment_percentage}%)>"
