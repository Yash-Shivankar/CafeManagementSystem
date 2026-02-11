from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from typing import List
from app.crud.base import CRUDBase
from app.core.database import get_db
from app.dependencies.auth import get_current_user
from app.schemas.inventory_log import (
    InventoryLogCreate,
    InventoryLogOut,
    InventoryLogUpdate,
    PaginatedInventoryLogOut,
)
from app.models.InventoryLogs import InventoryLog
from math import ceil

inventory_log_crud = CRUDBase[InventoryLog, InventoryLogCreate, InventoryLogUpdate](
    InventoryLog
)
router = APIRouter(
    prefix="/inventory-logs",
    tags=["Inventory Logs"],
)


@router.post("/", response_model=InventoryLogOut)
def add_inventory_log(
    obj_in: InventoryLogCreate,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    return inventory_log_crud.create(
        db=db,
        obj_in=obj_in,
        current_user=current_user,
    )


# @router.get("/", response_model=List[InventoryLogOut])
# def list_inventory_logs(
#     item_id: int | None = None,
#     db: Session = Depends(get_db),
# ):
#     query = db.query(InventoryLog).filter(InventoryLog.is_deleted == False)

#     if item_id:
#         query = query.filter(InventoryLog.item_id == item_id)

#     return query.order_by(InventoryLog.changed_on.desc()).all()


@router.get("/", response_model=PaginatedInventoryLogOut)
def list_inventory_logs(
    page: int = Query(1, ge=1),
    limit: int = Query(10, ge=1, le=100),
    db: Session = Depends(get_db),
):
    skip = (page - 1) * limit
    inventory_logs, total = inventory_log_crud.get_multi_paginated(
        db, skip=skip, limit=limit, relationships=["item"]
    )
    total_pages = ceil(total / limit)
    return {
        "data": inventory_logs,
        "total": total,
        "totalPages": total_pages,
        "currentPage": page,
    }
