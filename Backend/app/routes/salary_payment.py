from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List

from app.crud.base import CRUDBase
from app.models.SalaryPayment import SalaryPayment
from app.schemas.salary_payment import (
    SalaryPaymentCreate,
    SalaryPaymentUpdate,
    SalaryPaymentOut,
)
from app.core.database import get_db
from app.dependencies.auth import get_current_user

router = APIRouter(prefix="/salary-payments", tags=["SalaryPayments"])

salary_payment_crud = CRUDBase[SalaryPayment, SalaryPaymentCreate, SalaryPaymentUpdate](
    SalaryPayment
)


@router.post("/", response_model=SalaryPaymentOut)
def create_salary_payment(
    obj_in: SalaryPaymentCreate,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    return salary_payment_crud.create(
        db=db,
        obj_in=obj_in,
        current_user=current_user,
    )


@router.get("/{salary_payment_id}", response_model=SalaryPaymentOut)
def get_salary_payment(
    salary_payment_id: int,
    db: Session = Depends(get_db),
):
    return salary_payment_crud.get(db, salary_payment_id)


@router.get("/", response_model=List[SalaryPaymentOut])
def list_salary_payments(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
):
    return salary_payment_crud.get_multi(db, skip=skip, limit=limit)


@router.put("/{salary_payment_id}", response_model=SalaryPaymentOut)
def update_salary_payments(
    salary_payment_id: int,
    obj_in: SalaryPaymentUpdate,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    db_obj = salary_payment_crud.get(db, salary_payment_id)
    return salary_payment_crud.update(
        db=db,
        db_obj=db_obj,
        obj_in=obj_in,
        current_user=current_user,
    )


@router.delete("/{salary_payment_id}", response_model=SalaryPaymentOut)
def delete_salary_payment(
    salary_payment_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    return salary_payment_crud.remove(
        db=db,
        id=salary_payment_id,
        current_user=current_user,
    )
