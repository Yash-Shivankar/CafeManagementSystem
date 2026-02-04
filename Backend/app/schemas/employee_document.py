# app/schemas/employee_document.py
from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel
from app.schemas.employee_details import EmployeeDetailsOut


class EmployeeDocumentBase(BaseModel):
    filename: str
    employee_id: int
    doc_type: str
    doc_url: str
    original_name: str
    size: str


class EmployeeDocumentCreate(EmployeeDocumentBase):
    pass


class EmployeeDocumentUpdate(BaseModel):
    doc_type: Optional[str] = None
    doc_url: Optional[str] = None


class EmployeeDocumentOut(BaseModel):
    id: int
    employee: Optional[EmployeeDetailsOut]
    doc_type: str
    doc_url: str
    original_name: str
    size: str
    filename: str
    created_at: datetime
    updated_at: datetime
    created_by: Optional[int] = None
    updated_by: Optional[int] = None
    # deleted_at: Optional[datetime] = None
    # is_deleted: Optional[bool] = False

    class Config:
        from_attributes = True


class PaginatedEmployeeDocumentOut(BaseModel):
    data: List[EmployeeDocumentOut]
    total: int
    totalPages: int
    currentPage: int
