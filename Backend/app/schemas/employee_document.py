from datetime import datetime

from pydantic import BaseModel, ConfigDict

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
    doc_type: str | None = None
    doc_url: str | None = None


class EmployeeDocumentOut(BaseModel):
    id: int
    employee: EmployeeDetailsOut | None
    doc_type: str
    doc_url: str
    original_name: str
    size: str
    filename: str
    created_at: datetime
    updated_at: datetime
    created_by: int | None = None
    updated_by: int | None = None

    model_config = ConfigDict(from_attributes=True)


class PaginatedEmployeeDocumentOut(BaseModel):
    data: list[EmployeeDocumentOut]
    total: int
    totalPages: int
    currentPage: int
