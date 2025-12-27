# app/api/departments.py
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List
from app.crud.base import CRUDBase
from app.models.Department import Department
from app.schemas.department import DepartmentCreate, DepartmentUpdate, DepartmentOut
from app.core.database import get_db
from app.dependencies.auth import get_current_user

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


@router.get("/", response_model=List[DepartmentOut])
def list_departments(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return department_crud.get_multi(db, skip=skip, limit=limit)


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
