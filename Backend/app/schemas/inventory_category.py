from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class InventoryCategoryBase(BaseModel):
    category_name: str = Field(..., min_length=2, max_length=100)


class InventoryCategoryCreate(InventoryCategoryBase):
    pass


class InventoryCategoryUpdate(BaseModel):
    category_name: str | None = Field(default=None, min_length=2, max_length=100)


class InventoryCategoryOut(InventoryCategoryBase):
    id: int

    created_at: datetime
    updated_at: datetime
    created_by: int | None = None
    updated_by: int | None = None

    model_config = ConfigDict(from_attributes=True)


class PaginatedInventoryCategoryOut(BaseModel):
    data: list[InventoryCategoryOut]
    total: int
    totalPages: int
    currentPage: int
