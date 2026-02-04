from datetime import datetime
from typing import Optional, List
from decimal import Decimal

from pydantic import BaseModel, Field


class ServiceBase(BaseModel):
    name: str = Field(..., max_length=100, example="Table Decoration")
    price: Decimal = Field(..., gt=0, example=499.99)


class ServiceCreate(ServiceBase):
    """Schema for creating a service"""

    pass


class ServiceUpdate(BaseModel):
    """Schema for updating a service (partial update allowed)"""

    name: Optional[str] = Field(None, max_length=100)
    price: Optional[Decimal] = Field(None, gt=0)


class ServiceOut(ServiceBase):
    id: int

    created_at: datetime
    updated_at: datetime
    created_by: Optional[int] = None
    updated_by: Optional[int] = None
    # deleted_at: Optional[datetime] = None
    # is_deleted: Optional[bool] = False

    class Config:
        from_attributes = True


class PaginatedServiceOut(BaseModel):
    data: List[ServiceOut]
    total: int
    totalPages: int
    currentPage: int
