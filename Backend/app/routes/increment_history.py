from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from typing import List

from app.crud.base import CRUDBase
from app.models.IncrementHistory import IncrementHistory
from app.schemas.increment_history import (
    IncrementHistoryCreate,
    IncrementHistoryUpdate,
    IncrementHistoryOut,
    PaginatedIncrementHistoryOut,
)
from app.core.database import get_db
from app.dependencies.auth import get_current_user
from math import ceil

router = APIRouter(
    prefix="/increment-histories",
    tags=["Increment History"],
)

increment_crud = CRUDBase[
    IncrementHistory,
    IncrementHistoryCreate,
    IncrementHistoryUpdate,
](IncrementHistory)


@router.post("/", response_model=IncrementHistoryOut)
def create_increment(
    obj_in: IncrementHistoryCreate,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    return increment_crud.create(
        db=db,
        obj_in=obj_in,
        current_user=current_user,
    )


@router.get("/{increment_id}", response_model=IncrementHistoryOut)
def get_increment(
    increment_id: int,
    db: Session = Depends(get_db),
):
    return increment_crud.get(db, increment_id)


# @router.get("/", response_model=List[IncrementHistoryOut])
# def list_increments(
#     skip: int = 0,
#     limit: int = 100,
#     db: Session = Depends(get_db),
# ):
#     return increment_crud.get_multi(db, skip=skip, limit=limit)


@router.get("/", response_model=PaginatedIncrementHistoryOut)
def list_increments(
    page: int = Query(1, ge=1),
    limit: int = Query(10, ge=1, le=100),
    db: Session = Depends(get_db),
):
    skip = (page - 1) * limit
    increments, total = increment_crud.get_multi_paginated(db, skip=skip, limit=limit)
    total_pages = ceil(total / limit)
    return {
        "data": increments,
        "total": total,
        "totalPages": total_pages,
        "currentPage": page,
    }


@router.put("/{increment_id}", response_model=IncrementHistoryOut)
def update_increment(
    increment_id: int,
    obj_in: IncrementHistoryUpdate,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    db_obj = increment_crud.get(db, increment_id)
    return increment_crud.update(
        db=db,
        db_obj=db_obj,
        obj_in=obj_in,
        current_user=current_user,
    )


@router.delete("/{increment_id}", response_model=IncrementHistoryOut)
def delete_increment(
    increment_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    return increment_crud.remove(
        db=db,
        id=increment_id,
        current_user=current_user,
    )
