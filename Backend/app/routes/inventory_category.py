from fastapi import APIRouter, Depends
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
)

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


@router.get("/", response_model=List[InventoryCategoryOut])
def list_categories(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
):
    return category_crud.get_multi(
        db=db,
        skip=skip,
        limit=limit,
    )


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
