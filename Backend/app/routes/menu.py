"""Menu endpoints.

HTTP binding only. What may be on a menu is MenuItemService; how it is fetched
is MenuItemRepository.
"""

from decimal import Decimal

from fastapi import APIRouter, Depends, Query, status

from app.controllers.menuCategoryController import MenuCategoryController
from app.controllers.menuItemController import MenuItemController
from app.schemas.menu import (
    MenuCategoryCreate,
    MenuCategoryOut,
    MenuCategoryUpdate,
    MenuItemCreate,
    MenuItemOut,
    MenuItemUpdate,
    PaginatedMenuCategoryOut,
    PaginatedMenuItemOut,
)
from app.utils.pagination import PageParams, page_params

category_router = APIRouter(prefix="/menu-categories", tags=["Menu"])
item_router = APIRouter(prefix="/menu-items", tags=["Menu"])


@category_router.get("/", response_model=PaginatedMenuCategoryOut)
def list_categories(
    search: str | None = Query(None, min_length=1),
    is_active: bool | None = Query(None),
    params: PageParams = Depends(page_params),
    controller: MenuCategoryController = Depends(),
):
    return controller.list(params, search=search, is_active=is_active)


@category_router.get("/{category_id}", response_model=MenuCategoryOut)
def get_category(
    category_id: int,
    controller: MenuCategoryController = Depends(),
):
    return controller.get(category_id)


@category_router.post("/", response_model=MenuCategoryOut, status_code=status.HTTP_201_CREATED)
def create_category(
    payload: MenuCategoryCreate,
    controller: MenuCategoryController = Depends(),
):
    return controller.create(payload)


@category_router.put("/{category_id}", response_model=MenuCategoryOut)
def update_category(
    category_id: int,
    payload: MenuCategoryUpdate,
    controller: MenuCategoryController = Depends(),
):
    return controller.update(category_id, payload)


@category_router.delete("/{category_id}", response_model=MenuCategoryOut)
def delete_category(
    category_id: int,
    controller: MenuCategoryController = Depends(),
):
    return controller.delete(category_id)


@item_router.get("/", response_model=PaginatedMenuItemOut)
def list_items(
    search: str | None = Query(None, min_length=1),
    category_id: int | None = Query(None),
    is_veg: bool | None = Query(None),
    is_available: bool | None = Query(None),
    is_active: bool | None = Query(None),
    min_price: Decimal | None = Query(None, ge=0),
    max_price: Decimal | None = Query(None, ge=0),
    params: PageParams = Depends(page_params),
    controller: MenuItemController = Depends(),
):
    return controller.list(
        params,
        search=search,
        category_id=category_id,
        is_veg=is_veg,
        is_available=is_available,
        is_active=is_active,
        min_price=min_price,
        max_price=max_price,
    )


@item_router.get("/{item_id}", response_model=MenuItemOut)
def get_item(item_id: int, controller: MenuItemController = Depends()):
    return controller.get(item_id)


@item_router.post("/", response_model=MenuItemOut, status_code=status.HTTP_201_CREATED)
def create_item(
    payload: MenuItemCreate,
    controller: MenuItemController = Depends(),
):
    return controller.create(payload)


@item_router.put("/{item_id}", response_model=MenuItemOut)
def update_item(
    item_id: int,
    payload: MenuItemUpdate,
    controller: MenuItemController = Depends(),
):
    return controller.update(item_id, payload)


@item_router.delete("/{item_id}", response_model=MenuItemOut)
def delete_item(item_id: int, controller: MenuItemController = Depends()):
    return controller.delete(item_id)
