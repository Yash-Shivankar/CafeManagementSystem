# app/api/employee_performance.py
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List
from app.crud.base import CRUDBase
from app.models.EmployeePerformance import EmployeePerformance
from app.schemas.employee_performance import (
    EmployeePerformanceCreate,
    EmployeePerformanceUpdate,
    EmployeePerformanceOut,
)
from app.core.database import get_db
from app.dependencies.auth import get_current_user

router = APIRouter(prefix="/employee-performance", tags=["EmployeePerformances"])
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


@router.get("/", response_model=List[EmployeePerformanceOut])
def list_performances(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return performance_crud.get_multi(db, skip=skip, limit=limit)


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
