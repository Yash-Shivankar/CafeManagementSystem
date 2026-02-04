from datetime import datetime
from typing import Optional, List

from pydantic import BaseModel, Field


class TableBase(BaseModel):
    table_number: str = Field(..., max_length=20, example="T-01")
    seating_capacity: int = Field(..., gt=0, example=4)


class TableCreate(TableBase):
    pass


class TableUpdate(BaseModel):
    table_number: Optional[str] = Field(None, max_length=20)
    seating_capacity: Optional[int] = Field(None, gt=0)


class TableOut(TableBase):
    id: int

    created_at: datetime
    updated_at: datetime
    created_by: Optional[int] = None
    updated_by: Optional[int] = None
    deleted_at: Optional[datetime] = None
    is_deleted: Optional[bool] = False

    class Config:
        from_attributes = True


class PaginatedTableOut(BaseModel):
    data: List[TableOut]
    total: int
    totalPages: int
    currentPage: int
