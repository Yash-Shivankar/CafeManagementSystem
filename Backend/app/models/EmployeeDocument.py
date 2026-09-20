from sqlalchemy import (
    Column,
    ForeignKey,
    Index,
    Integer,
    String,
)
from sqlalchemy.orm import relationship

from app.models.Common import Common


class EmployeeDocument(Common):
    __tablename__ = "employee_documents"
    __table_args__ = (Index("ix_employee_documents_is_deleted", "is_deleted"),)

    id = Column(Integer, primary_key=True, index=True)

    employee_id = Column(
        Integer,
        ForeignKey("employee_details.id"),
        nullable=False,
    )
    filename = Column(String(255))
    doc_type = Column(String(100), nullable=False)
    doc_url = Column(String(255), nullable=False)
    original_name = Column(String(255))
    size = Column(String(100), nullable=False)

    employee = relationship(
        "EmployeeDetails",
        foreign_keys=[employee_id],
        back_populates="documents",
    )

    def __repr__(self):
        return f"<EmployeeDocument id={self.id} type={self.doc_type}>"
