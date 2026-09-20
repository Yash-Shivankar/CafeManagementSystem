from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

from app.models.Enums import InventoryChangeType
from app.schemas.inventory_item import InventoryItemOut


class InventoryLogBase(BaseModel):
    item_id: int
    change_type: InventoryChangeType

    quantity: int = Field(..., gt=0, description="Always positive number")
    reference: str | None = Field(default=None, max_length=100)


class InventoryLogCreate(InventoryLogBase):
    pass


class InventoryLogUpdate(InventoryLogBase):
    pass


class InventoryLogOut(BaseModel):
    id: int
    item: InventoryItemOut | None
    change_type: InventoryChangeType
    quantity: int = Field(..., gt=0, description="Always positive number")
    reference: str | None = Field(default=None, max_length=100)
    changed_on: datetime
    created_at: datetime
    updated_at: datetime
    created_by: int | None
    updated_by: int | None

    model_config = ConfigDict(from_attributes=True)


class PaginatedInventoryLogOut(BaseModel):
    data: list[InventoryLogOut]
    total: int
    totalPages: int
    currentPage: int
