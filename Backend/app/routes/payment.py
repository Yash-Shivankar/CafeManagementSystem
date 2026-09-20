"""Payments endpoints.

HTTP binding only: path, verb, response model. What happens next is
PaymentService; how it is fetched is PaymentRepository.
"""

from datetime import date

from fastapi import APIRouter, Depends, Query

from app.controllers.paymentController import PaymentController
from app.schemas.payment import (
    PaginatedPaymentOut,
    PaymentCreate,
    PaymentOut,
    PaymentUpdate,
)
from app.utils.pagination import PageParams, page_params

router = APIRouter(prefix="/payments", tags=["Payments"])


@router.get("/", response_model=PaginatedPaymentOut)
def list_payments(
    start_date: date | None = Query(None),
    end_date: date | None = Query(None),
    method: str | None = Query(None),
    search: str | None = Query(None, min_length=1),
    params: PageParams = Depends(page_params),
    controller: PaymentController = Depends(),
):
    return controller.list(
        params,
        search=search,
        start_date=start_date,
        end_date=end_date,
        method=method,
    )


@router.get("/{payment_id}", response_model=PaymentOut)
def get_payment(
    payment_id: int,
    controller: PaymentController = Depends(),
):
    return controller.get(payment_id)


@router.post("/", response_model=PaymentOut)
def create_payment(
    payload: PaymentCreate,
    controller: PaymentController = Depends(),
):
    return controller.create(payload)


@router.put("/{payment_id}", response_model=PaymentOut)
def update_payment(
    payment_id: int,
    payload: PaymentUpdate,
    controller: PaymentController = Depends(),
):
    return controller.update(payment_id, payload)


@router.delete("/{payment_id}", response_model=PaymentOut)
def delete_payment(
    payment_id: int,
    controller: PaymentController = Depends(),
):
    return controller.delete(payment_id)
