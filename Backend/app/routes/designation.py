# app/api/designations.py
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List
from app.crud.base import CRUDBase
from app.models.Designation import Designation
from app.schemas.designation import DesignationCreate, DesignationUpdate, DesignationOut
from app.core.database import get_db
from app.dependencies.auth import get_current_user

router = APIRouter(prefix="/designations", tags=["Designations"])
designation_crud = CRUDBase[Designation, DesignationCreate, DesignationUpdate](
    Designation
)


@router.post("/", response_model=DesignationOut)
def create_designation(
    designation_in: DesignationCreate,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    return designation_crud.create(db, obj_in=designation_in, current_user=current_user)


@router.get("/{designation_id}", response_model=DesignationOut)
def get_designation(designation_id: int, db: Session = Depends(get_db)):
    return designation_crud.get(db, designation_id)


@router.get("/", response_model=List[DesignationOut])
def list_designations(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return designation_crud.get_multi(db, skip=skip, limit=limit)


@router.put("/{designation_id}", response_model=DesignationOut)
def update_designation(
    designation_id: int,
    designation_in: DesignationUpdate,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    db_designation = designation_crud.get(db, designation_id)
    return designation_crud.update(
        db, db_designation, obj_in=designation_in, current_user=current_user
    )


@router.delete("/{designation_id}", response_model=DesignationOut)
def delete_designation(
    designation_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    return designation_crud.remove(db, designation_id, current_user=current_user)
