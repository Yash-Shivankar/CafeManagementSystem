"""Inventory Items endpoints.

HTTP binding only: path, verb, response model. What happens next is
InventoryItemService; how it is fetched is InventoryItemRepository.
"""

from fastapi import APIRouter, Depends, Query

from app.controllers.inventoryItemController import InventoryItemController
from app.schemas.inventory_item import (
    InventoryItemCreate,
    InventoryItemOut,
    InventoryItemUpdate,
    PaginatedInventoryItemOut,
)
from app.utils.pagination import PageParams, page_params

router = APIRouter(prefix="/inventory-items", tags=["Inventory Items"])


@router.get("/", response_model=PaginatedInventoryItemOut)
def list_items(
    category_id: int | None = Query(None),
    search: str | None = Query(None, min_length=1),
    params: PageParams = Depends(page_params),
    controller: InventoryItemController = Depends(),
):
    return controller.list(
        params,
        search=search,
        category_id=category_id,
    )


@router.get("/low-stock", response_model=PaginatedInventoryItemOut)
def list_low_stock(
    params: PageParams = Depends(page_params),
    controller: InventoryItemController = Depends(),
):
    """Items at or below their reorder level.

    Every item carries a reorder level, and this is the endpoint that compares
    stock against it. Without it `min_quantity` is a column nothing reads.

    Declared before `/{item_id}` on purpose: FastAPI matches routes in order,
    and `{item_id}: int` would reject "low-stock" with a 422 rather than
    falling through to this one.
    """
    return controller.low_stock(params)


@router.get("/{item_id}", response_model=InventoryItemOut)
def get_item(
    item_id: int,
    controller: InventoryItemController = Depends(),
):
    return controller.get(item_id)


@router.post("/", response_model=InventoryItemOut)
def create_item(
    payload: InventoryItemCreate,
    controller: InventoryItemController = Depends(),
):
    return controller.create(payload)


@router.put("/{item_id}", response_model=InventoryItemOut)
def update_item(
    item_id: int,
    payload: InventoryItemUpdate,
    controller: InventoryItemController = Depends(),
):
    return controller.update(item_id, payload)


@router.delete("/{item_id}", response_model=InventoryItemOut)
def delete_item(
    item_id: int,
    controller: InventoryItemController = Depends(),
):
    return controller.delete(item_id)
