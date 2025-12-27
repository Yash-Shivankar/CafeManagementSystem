# app/schemas/employee_document.py
from datetime import datetime
from typing import Optional
from pydantic import BaseModel


class EmployeeDocumentBase(BaseModel):
    employee_id: int
    doc_type: str
    doc_url: str


class EmployeeDocumentCreate(EmployeeDocumentBase):
    pass


class EmployeeDocumentUpdate(BaseModel):
    doc_type: Optional[str] = None
    doc_url: Optional[str] = None


class EmployeeDocumentOut(EmployeeDocumentBase):
    id: int
    created_at: datetime
    updated_at: datetime
    created_by: Optional[int] = None
    updated_by: Optional[int] = None
    deleted_at: Optional[datetime] = None
    is_deleted: Optional[bool] = False

    class Config:
        from_attributes = True
