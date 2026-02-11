from datetime import datetime
from typing import Optional, List

from pydantic import BaseModel, Field
from decimal import Decimal
from app.schemas.inventory_category import InventoryCategoryOut


class InventoryItemBase(BaseModel):
    name: str = Field(..., min_length=2, max_length=100)
    category_id: int

    quantity: int = Field(default=0, ge=0)
    min_quantity: int = Field(default=0, ge=0)

    cost_price: Decimal = Field(..., gt=0)
    selling_price: Decimal = Field(..., gt=0)


class InventoryItemCreate(InventoryItemBase):
    pass


class InventoryItemUpdate(BaseModel):
    name: Optional[str] = Field(default=None, min_length=2, max_length=100)
    category_id: Optional[int] = None

    quantity: Optional[int] = Field(default=None, ge=0)
    min_quantity: Optional[int] = Field(default=None, ge=0)

    cost_price: Optional[Decimal] = Field(default=None, gt=0)
    selling_price: Optional[Decimal] = Field(default=None, gt=0)


class InventoryItemOut(InventoryItemBase):
    id: int
    name: str = Field(..., min_length=2, max_length=100)
    category: Optional[InventoryCategoryOut]
    quantity: int = Field(default=0, ge=0)
    min_quantity: int = Field(default=0, ge=0)
    cost_price: Decimal = Field(..., gt=0)
    selling_price: Decimal = Field(..., gt=0)
    created_at: datetime
    updated_at: datetime
    created_by: Optional[int]
    updated_by: Optional[int]
    # deleted_at: Optional[datetime] = None
    # is_deleted: Optional[bool] = False

    class Config:
        from_attributes = True


class PaginatedInventoryItemOut(BaseModel):
    data: List[InventoryItemOut]
    total: int
    totalPages: int
    currentPage: int
