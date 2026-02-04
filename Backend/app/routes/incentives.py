from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from typing import List

from app.crud.base import CRUDBase
from app.models.Incentives import Incentives
from app.schemas.incentives import (
    IncentiveCreate,
    IncentiveUpdate,
    IncentiveOut,
    PaginatedIncentiveOut,
)
from app.core.database import get_db
from app.dependencies.auth import get_current_user
from math import ceil

router = APIRouter(prefix="/incentives", tags=["Incentives"])

incentive_crud = CRUDBase[Incentives, IncentiveCreate, IncentiveUpdate](Incentives)


@router.post("/", response_model=IncentiveOut)
def create_incentive(
    obj_in: IncentiveCreate,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    return incentive_crud.create(
        db=db,
        obj_in=obj_in,
        current_user=current_user,
    )


@router.get("/{incentive_id}", response_model=IncentiveOut)
def get_incentive(
    incentive_id: int,
    db: Session = Depends(get_db),
):
    return incentive_crud.get(db, incentive_id)


# @router.get("/", response_model=List[IncentiveOut])
# def list_incentives(
#     skip: int = 0,
#     limit: int = 100,
#     db: Session = Depends(get_db),
# ):
#     return incentive_crud.get_multi(db, skip=skip, limit=limit)


@router.get("/", response_model=PaginatedIncentiveOut)
def list_incentives(
    page: int = Query(1, ge=1),
    limit: int = Query(10, ge=1, le=100),
    db: Session = Depends(get_db),
):
    skip = (page - 1) * limit
    incentives, total = incentive_crud.get_multi_paginated(db, skip=skip, limit=limit)
    total_pages = ceil(total / limit)
    return {
        "data": incentives,
        "total": total,
        "totalPages": total_pages,
        "currentPage": page,
    }


@router.put("/{incentive_id}", response_model=IncentiveOut)
def update_incentive(
    incentive_id: int,
    obj_in: IncentiveUpdate,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    db_obj = incentive_crud.get(db, incentive_id)
    return incentive_crud.update(
        db=db,
        db_obj=db_obj,
        obj_in=obj_in,
        current_user=current_user,
    )


@router.delete("/{incentive_id}", response_model=IncentiveOut)
def delete_incentive(
    incentive_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    return incentive_crud.remove(
        db=db,
        id=incentive_id,
        current_user=current_user,
    )
