# app/api/payments.py
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from typing import List
from app.crud.base import CRUDBase
from app.models.Payment import Payment
from app.schemas.payment import (
    PaymentCreate,
    PaymentUpdate,
    PaymentOut,
    PaginatedPaymentOut,
)
from app.core.database import get_db
from app.dependencies.auth import get_current_user
from math import ceil

router = APIRouter(prefix="/payments", tags=["Payments"])
payment_crud = CRUDBase[Payment, PaymentCreate, PaymentUpdate](Payment)


@router.post("/", response_model=PaymentOut)
def create_payment(
    payment_in: PaymentCreate,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    return payment_crud.create(db, obj_in=payment_in, current_user=current_user)


@router.get("/{payment_id}", response_model=PaymentOut)
def get_payment(payment_id: int, db: Session = Depends(get_db)):
    return payment_crud.get(db, payment_id)


# @router.get("/", response_model=List[PaymentOut])
# def list_payments(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
#     return payment_crud.get_multi(db, skip=skip, limit=limit)


@router.get("/", response_model=PaginatedPaymentOut)
def list_payments(
    page: int = Query(1, ge=1),
    limit: int = Query(10, ge=1, le=100),
    db: Session = Depends(get_db),
):
    skip = (page - 1) * limit
    payments, total = payment_crud.get_multi_paginated(db, skip=skip, limit=limit)
    total_pages = ceil(total / limit)
    return {
        "data": payments,
        "total": total,
        "totalPages": total_pages,
        "currentPage": page,
    }


@router.put("/{payment_id}", response_model=PaymentOut)
def update_payment(
    payment_id: int,
    payment_in: PaymentUpdate,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    db_payment = payment_crud.get(db, payment_id)
    return payment_crud.update(
        db, db_payment, obj_in=payment_in, current_user=current_user
    )


@router.delete("/{payment_id}", response_model=PaymentOut)
def delete_payment(
    payment_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    return payment_crud.remove(db, payment_id, current_user=current_user)
