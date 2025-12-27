from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List

from app.crud.base import CRUDBase
from app.models.SalaryStructure import SalaryStructure
from app.schemas.salary_structure import (
    SalaryStructureCreate,
    SalaryStructureUpdate,
    SalaryStructureOut,
)
from app.core.database import get_db
from app.dependencies.auth import get_current_user

router = APIRouter(prefix="/salary-structures", tags=["SalaryStructures"])

salary_structure_crud = CRUDBase[
    SalaryStructure, SalaryStructureCreate, SalaryStructureUpdate
](SalaryStructure)


@router.post("/", response_model=SalaryStructureOut)
def create_salary_structure(
    obj_in: SalaryStructureCreate,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    return salary_structure_crud.create(
        db=db,
        obj_in=obj_in,
        current_user=current_user,
    )


@router.get("/{salary_structure_id}", response_model=SalaryStructureOut)
def get_salary_structure(
    salary_structure_id: int,
    db: Session = Depends(get_db),
):
    return salary_structure_crud.get(db, salary_structure_id)


@router.get("/", response_model=List[SalaryStructureOut])
def list_salary_structure(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
):
    return salary_structure_crud.get_multi(db, skip=skip, limit=limit)


@router.put("/{salary_structure_id}", response_model=SalaryStructureOut)
def update_salary_structure(
    salary_structure_id: int,
    obj_in: SalaryStructureUpdate,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    db_obj = salary_structure_crud.get(db, salary_structure_id)
    return salary_structure_crud.update(
        db=db,
        db_obj=db_obj,
        obj_in=obj_in,
        current_user=current_user,
    )


@router.delete("/{salary_structure_id}", response_model=SalaryStructureOut)
def delete_salary_structure(
    salary_structure_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    return salary_structure_crud.remove(
        db=db,
        id=salary_structure_id,
        current_user=current_user,
    )
