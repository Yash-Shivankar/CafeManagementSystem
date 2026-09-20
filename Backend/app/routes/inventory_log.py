"""Inventory Logs endpoints.

Append-only ledger: create and read, no update or delete. See
InventoryLogService for why.
"""

from fastapi import APIRouter, Depends, Query

from app.controllers.inventoryLogController import InventoryLogController
from app.schemas.inventory_log import (
    InventoryLogCreate,
    InventoryLogOut,
    PaginatedInventoryLogOut,
)
from app.utils.pagination import PageParams, page_params

router = APIRouter(prefix="/inventory-logs", tags=["Inventory Logs"])


@router.get("/", response_model=PaginatedInventoryLogOut)
def list_inventory_logs(
    item_id: int | None = Query(None),
    change_type: str | None = Query(None),
    params: PageParams = Depends(page_params),
    controller: InventoryLogController = Depends(),
):
    return controller.list(params, item_id=item_id, change_type=change_type)


@router.post("/", response_model=InventoryLogOut)
def add_inventory_log(
    payload: InventoryLogCreate,
    controller: InventoryLogController = Depends(),
):
    return controller.create(payload)
