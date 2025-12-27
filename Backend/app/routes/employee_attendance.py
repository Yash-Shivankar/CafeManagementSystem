# app/api/employee_attendance.py
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List
from app.crud.base import CRUDBase
from app.models.EmployeeAttendance import EmployeeAttendance
from app.schemas.employee_attendance import (
    EmployeeAttendanceCreate,
    EmployeeAttendanceUpdate,
    EmployeeAttendanceOut,
)
from app.core.database import get_db
from app.dependencies.auth import get_current_user

router = APIRouter(prefix="/employee-attendance", tags=["EmployeeAttendances"])
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


@router.get("/", response_model=List[EmployeeAttendanceOut])
def list_attendance(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return attendance_crud.get_multi(db, skip=skip, limit=limit)


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
