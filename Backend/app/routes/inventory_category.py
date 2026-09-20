"""Inventory Categories endpoints.

HTTP binding only: path, verb, response model. What happens next is
InventoryCategoryService; how it is fetched is InventoryCategoryRepository.
"""

from fastapi import APIRouter, Depends, Query

from app.controllers.inventoryCategoryController import InventoryCategoryController
from app.schemas.inventory_category import (
    InventoryCategoryCreate,
    InventoryCategoryOut,
    InventoryCategoryUpdate,
    PaginatedInventoryCategoryOut,
)
from app.utils.pagination import PageParams, page_params

router = APIRouter(prefix="/inventory-categories", tags=["Inventory Categories"])


@router.get("/", response_model=PaginatedInventoryCategoryOut)
def list_categories(
    search: str | None = Query(None, min_length=1),
    params: PageParams = Depends(page_params),
    controller: InventoryCategoryController = Depends(),
):
    return controller.list(
        params,
        search=search,
    )


@router.get("/{category_id}", response_model=InventoryCategoryOut)
def get_category(
    category_id: int,
    controller: InventoryCategoryController = Depends(),
):
    return controller.get(category_id)


@router.post("/", response_model=InventoryCategoryOut)
def create_category(
    payload: InventoryCategoryCreate,
    controller: InventoryCategoryController = Depends(),
):
    return controller.create(payload)


@router.put("/{category_id}", response_model=InventoryCategoryOut)
def update_category(
    category_id: int,
    payload: InventoryCategoryUpdate,
    controller: InventoryCategoryController = Depends(),
):
    return controller.update(category_id, payload)


@router.delete("/{category_id}", response_model=InventoryCategoryOut)
def delete_category(
    category_id: int,
    controller: InventoryCategoryController = Depends(),
):
    return controller.delete(category_id)
