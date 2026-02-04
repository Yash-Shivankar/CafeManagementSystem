from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from typing import List

from app.crud.base import CRUDBase
from app.models.ProfitLoss import ProfitLoss
from app.schemas.profit_loss import (
    ProfitLossCreate,
    ProfitLossUpdate,
    ProfitLossOut,
    PaginatedProfitLossOut,
)
from app.core.database import get_db
from app.dependencies.auth import get_current_user
from math import ceil

router = APIRouter(prefix="/profit-loss", tags=["ProfitLoss"])

profit_loss_crud = CRUDBase[ProfitLoss, ProfitLossCreate, ProfitLossUpdate](ProfitLoss)


@router.post("/", response_model=ProfitLossOut)
def create_profit_loss(
    obj_in: ProfitLossCreate,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    return profit_loss_crud.create(
        db=db,
        obj_in=obj_in,
        current_user=current_user,
    )


@router.get("/{profit_loss_id}", response_model=ProfitLossOut)
def get_profit_loss(
    profit_loss_id: int,
    db: Session = Depends(get_db),
):
    return profit_loss_crud.get(db, profit_loss_id)


# @router.get("/", response_model=List[ProfitLossOut])
# def list_profit_loss(
#     skip: int = 0,
#     limit: int = 100,
#     db: Session = Depends(get_db),
# ):
#     return profit_loss_crud.get_multi(db, skip=skip, limit=limit)


@router.get("/", response_model=PaginatedProfitLossOut)
def list_profit_loss(
    page: int = Query(1, ge=1),
    limit: int = Query(10, ge=1, le=100),
    db: Session = Depends(get_db),
):
    skip = (page - 1) * limit
    profit_loss, total = profit_loss_crud.get_multi_paginated(
        db, skip=skip, limit=limit
    )
    total_pages = ceil(total / limit)
    return {
        "data": profit_loss,
        "total": total,
        "totalPages": total_pages,
        "currentPage": page,
    }


@router.put("/{profit_loss_id}", response_model=ProfitLossOut)
def update_profit_loss(
    profit_loss_id: int,
    obj_in: ProfitLossUpdate,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    db_obj = profit_loss_crud.get(db, profit_loss_id)
    return profit_loss_crud.update(
        db=db,
        db_obj=db_obj,
        obj_in=obj_in,
        current_user=current_user,
    )


@router.delete("/{profit_loss_id}", response_model=ProfitLossOut)
def delete_profit_loss(
    profit_loss_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    return profit_loss_crud.remove(
        db=db,
        id=profit_loss_id,
        current_user=current_user,
    )
