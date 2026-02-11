from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field
from app.schemas.inventory_item import InventoryItemOut
from app.models.Enums import InventoryChangeType


class InventoryLogBase(BaseModel):
    item_id: int
    change_type: InventoryChangeType

    quantity: int = Field(..., gt=0, description="Always positive number")
    reference: Optional[str] = Field(default=None, max_length=100)


class InventoryLogCreate(InventoryLogBase):
    pass


class InventoryLogUpdate(InventoryLogBase):
    pass


class InventoryLogOut(BaseModel):
    id: int
    item: Optional[InventoryItemOut]
    change_type: InventoryChangeType
    quantity: int = Field(..., gt=0, description="Always positive number")
    reference: Optional[str] = Field(default=None, max_length=100)
    changed_on: datetime
    created_at: datetime
    updated_at: datetime
    created_by: Optional[int]
    updated_by: Optional[int]

    class Config:
        from_attributes = True


class PaginatedInventoryLogOut(BaseModel):
    data: List[InventoryLogOut]
    total: int
    totalPages: int
    currentPage: int
