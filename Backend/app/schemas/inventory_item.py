from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field

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
    name: str | None = Field(default=None, min_length=2, max_length=100)
    category_id: int | None = None

    quantity: int | None = Field(default=None, ge=0)
    min_quantity: int | None = Field(default=None, ge=0)

    cost_price: Decimal | None = Field(default=None, gt=0)
    selling_price: Decimal | None = Field(default=None, gt=0)


class InventoryItemOut(InventoryItemBase):
    id: int
    name: str = Field(..., min_length=2, max_length=100)
    category: InventoryCategoryOut | None
    quantity: int = Field(default=0, ge=0)
    min_quantity: int = Field(default=0, ge=0)
    cost_price: Decimal = Field(..., gt=0)
    selling_price: Decimal = Field(..., gt=0)
    created_at: datetime
    updated_at: datetime
    created_by: int | None
    updated_by: int | None

    model_config = ConfigDict(from_attributes=True)


class PaginatedInventoryItemOut(BaseModel):
    data: list[InventoryItemOut]
    total: int
    totalPages: int
    currentPage: int
