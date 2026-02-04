from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List

from app.core.database import get_db
from app.dependencies.auth import get_current_user
from app.crud.base import CRUDBase
from app.models.InventoryItem import InventoryItem
from app.schemas.inventory_item import (
    InventoryItemCreate,
    InventoryItemUpdate,
    InventoryItemOut,
    PaginatedInventoryItemOut,
)
from math import ceil

router = APIRouter(
    prefix="/inventory-items",
    tags=["Inventory Items"],
)

item_crud = CRUDBase[
    InventoryItem,
    InventoryItemCreate,
    InventoryItemUpdate,
](InventoryItem)


@router.post("/", response_model=InventoryItemOut)
def create_inventory_item(
    obj_in: InventoryItemCreate,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    return item_crud.create(
        db=db,
        obj_in=obj_in,
        current_user=current_user,
    )


@router.get("/{item_id}", response_model=InventoryItemOut)
def get_inventory_item(
    item_id: int,
    db: Session = Depends(get_db),
):
    return item_crud.get(db, item_id)


# @router.get("/", response_model=List[InventoryItemOut])
# def list_inventory_items(
#     skip: int = 0,
#     limit: int = 100,
#     category_id: int | None = None,
#     db: Session = Depends(get_db),
# ):
#     query = db.query(InventoryItem).filter(InventoryItem.is_deleted == False)

#     if category_id:
#         query = query.filter(InventoryItem.category_id == category_id)

#     return query.offset(skip).limit(limit).all()


@router.get("/", response_model=PaginatedInventoryItemOut)
def list_inventory_items(
    page: int = Query(1, ge=1),
    limit: int = Query(10, ge=1, le=100),
    db: Session = Depends(get_db),
):
    skip = (page - 1) * limit
    inventory_items, total = item_crud.get_multi_paginated(db, skip=skip, limit=limit)
    total_pages = ceil(total / limit)
    return {
        "data": inventory_items,
        "total": total,
        "totalPages": total_pages,
        "currentPage": page,
    }


@router.put("/{item_id}", response_model=InventoryItemOut)
def update_inventory_item(
    item_id: int,
    obj_in: InventoryItemUpdate,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    db_obj = item_crud.get(db, item_id)
    return item_crud.update(
        db=db,
        db_obj=db_obj,
        obj_in=obj_in,
        current_user=current_user,
    )


@router.delete("/{item_id}", response_model=InventoryItemOut)
def delete_inventory_item(
    item_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    return item_crud.remove(
        db=db,
        id=item_id,
        current_user=current_user,
    )
