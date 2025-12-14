from sqlalchemy import (
    Column,
    Integer,
    String,
    ForeignKey,
)
from sqlalchemy.orm import relationship
from app.models.Common import Common


class EmployeeDocument(Common):
    __tablename__ = "employee_documents"

    id = Column(Integer, primary_key=True, index=True)

    employee_id = Column(
        Integer,
        ForeignKey("employee_details.id"),
        nullable=False,
    )

    doc_type = Column(String(100), nullable=False)  # Aadhaar, PAN, Resume, etc.
    doc_url = Column(String(255), nullable=False)

    employee = relationship(
        "EmployeeDetails",
        foreign_keys=[employee_id],
        back_populates="documents",
    )

    def __repr__(self):
        return f"<EmployeeDocument id={self.id} type={self.doc_type}>"
