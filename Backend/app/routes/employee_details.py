# app/api/employee_details.py
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from typing import List
from app.crud.base import CRUDBase
from app.models.EmployeeDetails import EmployeeDetails
from app.schemas.employee_details import (
    EmployeeDetailsCreate,
    EmployeeDetailsUpdate,
    EmployeeDetailsOut,
    PaginatedEmployeeDetailsOut,
)
from app.core.database import get_db
from app.dependencies.auth import get_current_user
from math import ceil

router = APIRouter(prefix="/employee-details", tags=["EmployeeDetails"])
employee_crud = CRUDBase[EmployeeDetails, EmployeeDetailsCreate, EmployeeDetailsUpdate](
    EmployeeDetails
)


@router.post("/", response_model=EmployeeDetailsOut)
def create_employee(
    obj_in: EmployeeDetailsCreate,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    return employee_crud.create(db, obj_in=obj_in, current_user=current_user)


@router.get("/{employee_id}", response_model=EmployeeDetailsOut)
def get_employee(employee_id: int, db: Session = Depends(get_db)):
    return employee_crud.get(db, employee_id)


# @router.get("/", response_model=List[EmployeeDetailsOut])
# def list_employees(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
#     return employee_crud.get_multi(db, skip=skip, limit=limit)


@router.get("/", response_model=PaginatedEmployeeDetailsOut)
def list_employees(
    page: int = Query(1, ge=1),
    limit: int = Query(10, ge=1, le=100),
    db: Session = Depends(get_db),
):
    skip = (page - 1) * limit
    employees, total = employee_crud.get_multi_paginated(
        db,
        skip=skip,
        limit=limit,
        relationships=["department", "designation", "user"],
    )
    total_pages = ceil(total / limit)
    return {
        "data": employees,
        "total": total,
        "totalPages": total_pages,
        "currentPage": page,
    }


@router.put("/{employee_id}", response_model=EmployeeDetailsOut)
def update_employee(
    employee_id: int,
    obj_in: EmployeeDetailsUpdate,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    db_obj = employee_crud.get(db, employee_id)
    return employee_crud.update(db, db_obj, obj_in=obj_in, current_user=current_user)


@router.delete("/{employee_id}", response_model=EmployeeDetailsOut)
def delete_employee(
    employee_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    return employee_crud.remove(db, employee_id, current_user=current_user)
