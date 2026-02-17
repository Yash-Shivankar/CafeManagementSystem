# app/api/employee_performance.py
from fastapi import APIRouter, Depends, Query
from sqlalchemy import or_
from sqlalchemy.orm import Session
from typing import List
from app.crud.base import CRUDBase
from app.models.EmployeePerformance import EmployeePerformance
from app.models.EmployeeDetails import EmployeeDetails
from app.models.User import User
from app.schemas.employee_performance import (
    EmployeePerformanceCreate,
    EmployeePerformanceUpdate,
    EmployeePerformanceOut,
    PaginatedEmployeePerformanceOut,
)
from app.core.database import get_db
from app.dependencies.auth import get_current_user
from math import ceil

router = APIRouter(prefix="/employee-performances", tags=["EmployeePerformances"])
performance_crud = CRUDBase[
    EmployeePerformance, EmployeePerformanceCreate, EmployeePerformanceUpdate
](EmployeePerformance)


@router.post("/", response_model=EmployeePerformanceOut)
def create_performance(
    obj_in: EmployeePerformanceCreate,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    return performance_crud.create(db, obj_in=obj_in, current_user=current_user)


@router.get("/{performance_id}", response_model=EmployeePerformanceOut)
def get_performance(performance_id: int, db: Session = Depends(get_db)):
    return performance_crud.get(db, performance_id)


# @router.get("/", response_model=List[EmployeePerformanceOut])
# def list_performances(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
#     return performance_crud.get_multi(db, skip=skip, limit=limit)


@router.get("/", response_model=PaginatedEmployeePerformanceOut)
def list_performances(
    page: int = Query(1, ge=1),
    limit: int = Query(10, ge=1, le=100),
    rating: str | None = Query(None),
    search: str | None = Query(None, min_length=1),
    db: Session = Depends(get_db),
):
    skip = (page - 1) * limit

    filters = []

    if rating:
        filters.append(EmployeePerformance.rating == rating)

    if search:
        filters.append(
            or_(
                EmployeePerformance.feedback.ilike(f"%{search}%"),
                EmployeePerformance.employee.has(
                    EmployeeDetails.user.has(
                        or_(
                            User.first_name.ilike(f"%{search}%"),
                            User.last_name.ilike(f"%{search}%"),
                        )
                    ),
                ),
            )
        )

    performances, total = performance_crud.get_multi_paginated(
        db, skip=skip, limit=limit, filters=filters, relationships=["employee"]
    )
    total_pages = ceil(total / limit)
    return {
        "data": performances,
        "total": total,
        "totalPages": total_pages,
        "currentPage": page,
    }


@router.put("/{performance_id}", response_model=EmployeePerformanceOut)
def update_performance(
    performance_id: int,
    obj_in: EmployeePerformanceUpdate,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    db_obj = performance_crud.get(db, performance_id)
    return performance_crud.update(db, db_obj, obj_in=obj_in, current_user=current_user)


@router.delete("/{performance_id}", response_model=EmployeePerformanceOut)
def delete_performance(
    performance_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    return performance_crud.remove(db, performance_id, current_user=current_user)
