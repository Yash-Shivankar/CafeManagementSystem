from datetime import datetime
from typing import Optional, List

from pydantic import BaseModel, Field


class InventoryCategoryBase(BaseModel):
    category_name: str = Field(..., min_length=2, max_length=100)


class InventoryCategoryCreate(InventoryCategoryBase):
    pass


class InventoryCategoryUpdate(BaseModel):
    category_name: Optional[str] = Field(default=None, min_length=2, max_length=100)


class InventoryCategoryOut(InventoryCategoryBase):
    id: int

    created_at: datetime
    updated_at: datetime
    created_by: Optional[int] = None
    updated_by: Optional[int] = None
    # deleted_at: Optional[datetime] = None
    # is_deleted: Optional[bool] = False

    class Config:
        from_attributes = True


class PaginatedInventoryCategoryOut(BaseModel):
    data: List[InventoryCategoryOut]
    total: int
    totalPages: int
    currentPage: int
