# app/api/departments.py
from fastapi import APIRouter, Depends, Query
from sqlalchemy import or_
from sqlalchemy.orm import Session
from typing import List
from app.crud.base import CRUDBase
from app.models.Department import Department
from app.schemas.department import (
    DepartmentCreate,
    DepartmentUpdate,
    DepartmentOut,
    PaginatedDepartmentOut,
)
from app.core.database import get_db
from app.dependencies.auth import get_current_user
from math import ceil

router = APIRouter(prefix="/departments", tags=["Deplartments"])
department_crud = CRUDBase[Department, DepartmentCreate, DepartmentUpdate](Department)


@router.post("/", response_model=DepartmentOut)
def create_department(
    dept_in: DepartmentCreate,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    return department_crud.create(db, obj_in=dept_in, current_user=current_user)


@router.get("/{dept_id}", response_model=DepartmentOut)
def get_department(dept_id: int, db: Session = Depends(get_db)):
    return department_crud.get(db, dept_id)


# @router.get("/", response_model=List[DepartmentOut])
# def list_departments(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
#     return department_crud.get_multi(db, skip=skip, limit=limit)


@router.get("/", response_model=PaginatedDepartmentOut)
def list_departments(
    page: int = Query(1, ge=1),
    limit: int = Query(10, ge=1, le=100),
    search: str | None = Query(None, min_length=1),
    db: Session = Depends(get_db),
):
    skip = (page - 1) * limit

    filters = []
    if search:
        filters.append(or_(Department.department_name.ilike(f"%{search}%")))

    departments, total = department_crud.get_multi_paginated(
        db,
        skip=skip,
        limit=limit,
        filters=filters,
    )
    total_pages = ceil(total / limit)
    return {
        "data": departments,
        "total": total,
        "totalPages": total_pages,
        "currentPage": page,
    }


@router.put("/{dept_id}", response_model=DepartmentOut)
def update_department(
    dept_id: int,
    dept_in: DepartmentUpdate,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    db_dept = department_crud.get(db, dept_id)
    return department_crud.update(
        db, db_dept, obj_in=dept_in, current_user=current_user
    )


@router.delete("/{dept_id}", response_model=DepartmentOut)
def delete_department(
    dept_id: int, db: Session = Depends(get_db), current_user=Depends(get_current_user)
):
    return department_crud.remove(db, dept_id, current_user=current_user)
