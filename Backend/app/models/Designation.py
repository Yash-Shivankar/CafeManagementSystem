from sqlalchemy import (
    Column,
    Index,
    Integer,
    String,
)
from sqlalchemy.orm import relationship

from app.models.Common import Common


class Designation(Common):
    __tablename__ = "designations"
    __table_args__ = (Index("ix_designations_is_deleted", "is_deleted"),)

    id = Column(Integer, primary_key=True, index=True)
    designation_name = Column(String(255), nullable=False, unique=True)

    employees = relationship(
        "EmployeeDetails",
        foreign_keys="EmployeeDetails.designation_id",
        back_populates="designation",
        cascade="all, delete-orphan",
    )

    def __repr__(self):
        return f"<Designation id={self.id} designation_name={self.designation_name}>"
