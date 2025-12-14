from sqlalchemy import (
    Column,
    Integer,
    String,
)
from sqlalchemy.orm import relationship
from app.models.Common import Common


class Department(Common):
    __tablename__ = "departments"

    id = Column(Integer, primary_key=True, index=True)
    department_name = Column(String(255), nullable=False, unique=True)

    employees = relationship(
        "EmployeeDetails",
        foreign_keys="EmployeeDetails.department_id",
        back_populates="department",
        cascade="all, delete-orphan",
    )

    def __repr__(self):
        return f"<Department id={self.id} department_name={self.department_name}>"
