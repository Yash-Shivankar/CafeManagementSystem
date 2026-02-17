# app/api/employee_attendance.py
from fastapi import APIRouter, Depends, Query
from sqlalchemy import or_
from sqlalchemy.orm import Session
from datetime import date
from typing import List
from app.crud.base import CRUDBase
from app.models.EmployeeAttendance import EmployeeAttendance
from app.models.EmployeeDetails import EmployeeDetails
from app.models.User import User
from app.schemas.employee_attendance import (
    EmployeeAttendanceCreate,
    EmployeeAttendanceUpdate,
    EmployeeAttendanceOut,
    PaginatedEmployeeAttendanceOut,
)
from app.core.database import get_db
from app.dependencies.auth import get_current_user
from math import ceil

router = APIRouter(prefix="/employee-attendances", tags=["EmployeeAttendances"])
attendance_crud = CRUDBase[
    EmployeeAttendance, EmployeeAttendanceCreate, EmployeeAttendanceUpdate
](EmployeeAttendance)


@router.post("/", response_model=EmployeeAttendanceOut)
def create_attendance(
    attendance_in: EmployeeAttendanceCreate,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    return attendance_crud.create(db, obj_in=attendance_in, current_user=current_user)


@router.get("/{attendance_id}", response_model=EmployeeAttendanceOut)
def get_attendance(attendance_id: int, db: Session = Depends(get_db)):
    return attendance_crud.get(db, attendance_id)


# @router.get("/", response_model=List[EmployeeAttendanceOut])
# def list_attendance(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
#     return attendance_crud.get_multi(db, skip=skip, limit=limit)


@router.get("/", response_model=PaginatedEmployeeAttendanceOut)
def list_attendance(
    page: int = Query(1, ge=1),
    limit: int = Query(10, ge=1, le=100),
    start_date: date | None = Query(None),
    end_date: date | None = Query(None),
    status: str | None = Query(None),
    session: str | None = Query(None),
    search: str | None = Query(None, min_length=1),
    db: Session = Depends(get_db),
):
    skip = (page - 1) * limit

    filters = []

    if start_date:
        filters.append(EmployeeAttendance.date >= start_date)

    if end_date:
        filters.append(EmployeeAttendance.date <= end_date)
    if session:
        filters.append(EmployeeAttendance.session == session)
    if status:
        filters.append(EmployeeAttendance.status == status)

    if search:
        filters.append(
            or_(
                EmployeeAttendance.employee.has(
                    EmployeeDetails.user.has(
                        or_(
                            User.first_name.ilike(f"%{search}%"),
                            User.last_name.ilike(f"%{search}%"),
                        )
                    ),
                )
            )
        )

    attendances, total = attendance_crud.get_multi_paginated(
        db, skip=skip, limit=limit, filters=filters, relationships=["employee"]
    )
    total_pages = ceil(total / limit)
    return {
        "data": attendances,
        "total": total,
        "totalPages": total_pages,
        "currentPage": page,
    }


@router.put("/{attendance_id}", response_model=EmployeeAttendanceOut)
def update_attendance(
    attendance_id: int,
    attendance_in: EmployeeAttendanceUpdate,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    db_attendance = attendance_crud.get(db, attendance_id)
    return attendance_crud.update(
        db, db_attendance, obj_in=attendance_in, current_user=current_user
    )


@router.delete("/{attendance_id}", response_model=EmployeeAttendanceOut)
def delete_attendance(
    attendance_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    return attendance_crud.remove(db, attendance_id, current_user=current_user)
