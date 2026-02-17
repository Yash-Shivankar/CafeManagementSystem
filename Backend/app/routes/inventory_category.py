from fastapi import APIRouter, Depends, Query
from sqlalchemy import or_
from sqlalchemy.orm import Session
from typing import List

from app.core.database import get_db
from app.dependencies.auth import get_current_user
from app.crud.base import CRUDBase
from app.models.InventoryCategory import InventoryCategory
from app.schemas.inventory_category import (
    InventoryCategoryCreate,
    InventoryCategoryUpdate,
    InventoryCategoryOut,
    PaginatedInventoryCategoryOut,
)
from math import ceil

router = APIRouter(
    prefix="/inventory-categories",
    tags=["Inventory Categories"],
)

category_crud = CRUDBase[
    InventoryCategory,
    InventoryCategoryCreate,
    InventoryCategoryUpdate,
](InventoryCategory)


@router.post("/", response_model=InventoryCategoryOut)
def create_category(
    obj_in: InventoryCategoryCreate,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    return category_crud.create(
        db=db,
        obj_in=obj_in,
        current_user=current_user,
    )


@router.get("/{category_id}", response_model=InventoryCategoryOut)
def get_category(
    category_id: int,
    db: Session = Depends(get_db),
):
    return category_crud.get(db, category_id)


# @router.get("/", response_model=List[InventoryCategoryOut])
# def list_categories(
#     skip: int = 0,
#     limit: int = 100,
#     db: Session = Depends(get_db),
# ):
#     return category_crud.get_multi(
#         db=db,
#         skip=skip,
#         limit=limit,
#     )


@router.get("/", response_model=PaginatedInventoryCategoryOut)
def list_categories(
    page: int = Query(1, ge=1),
    limit: int = Query(10, ge=1, le=100),
    search: str | None = Query(None, min_length=1),
    db: Session = Depends(get_db),
):
    skip = (page - 1) * limit

    filters = []
    if search:
        filters.append(or_(InventoryCategory.category_name.ilike(f"%{search}%")))

    categories, total = category_crud.get_multi_paginated(
        db, skip=skip, limit=limit, filters=filters
    )
    total_pages = ceil(total / limit)
    return {
        "data": categories,
        "total": total,
        "totalPages": total_pages,
        "currentPage": page,
    }


@router.put("/{category_id}", response_model=InventoryCategoryOut)
def update_category(
    category_id: int,
    obj_in: InventoryCategoryUpdate,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    db_obj = category_crud.get(db, category_id)
    return category_crud.update(
        db=db,
        db_obj=db_obj,
        obj_in=obj_in,
        current_user=current_user,
    )


@router.delete("/{category_id}", response_model=InventoryCategoryOut)
def delete_category(
    category_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    return category_crud.remove(
        db=db,
        id=category_id,
        current_user=current_user,
    )
