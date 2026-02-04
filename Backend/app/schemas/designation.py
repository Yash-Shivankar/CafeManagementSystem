# app/schemas/designation.py
from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel


class DesignationBase(BaseModel):
    designation_name: str


class DesignationCreate(DesignationBase):
    pass


class DesignationUpdate(BaseModel):
    designation_name: Optional[str] = None


class DesignationOut(DesignationBase):
    id: int
    # created_at: datetime
    # updated_at: datetime
    # created_by: Optional[int] = None
    # updated_by: Optional[int] = None
    # deleted_at: Optional[datetime] = None
    # is_deleted: Optional[bool] = False

    class Config:
        from_attributes = True


class PaginatedDesignationOut(BaseModel):
    data: List[DesignationOut]
    total: int
    totalPages: int
    currentPage: int
