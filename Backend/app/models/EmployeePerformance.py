from sqlalchemy import (
    CheckConstraint,
    Column,
    DateTime,
    ForeignKey,
    Index,
    Integer,
    Text,
    func,
)
from sqlalchemy.orm import relationship

from app.models.Common import Common


class EmployeePerformance(Common):
    __tablename__ = "employee_performance"
    __table_args__ = (
        CheckConstraint("rating >= 1 AND rating <= 5", name="ck_rating_range"),
        Index("ix_employee_performance_is_deleted", "is_deleted"),
    )

    id = Column(Integer, primary_key=True, index=True)

    employee_id = Column(
        Integer,
        ForeignKey("employee_details.id"),
        nullable=False,
    )

    rating = Column(Integer, nullable=False)
    feedback = Column(Text, nullable=True)
    review_date = Column(DateTime(timezone=True), server_default=func.now())

    employee = relationship(
        "EmployeeDetails",
        foreign_keys=[employee_id],
        back_populates="performance_reviews",
    )

    def __repr__(self):
        return f"<EmployeePerformance emp={self.employee_id} rating={self.rating}>"
