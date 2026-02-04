# app/api/customer_invoices.py
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from typing import List
from app.crud.base import CRUDBase
from app.models.CustomerInvoice import CustomerInvoice
from app.schemas.customer_invoice import (
    CustomerInvoiceCreate,
    CustomerInvoiceUpdate,
    CustomerInvoiceOut,
    PaginatedCustomerInvoiceOut,
)
from app.core.database import get_db
from app.dependencies.auth import get_current_user
from math import ceil

router = APIRouter(prefix="/customer-invoices", tags=["CustomerInvoices"])
invoice_crud = CRUDBase[CustomerInvoice, CustomerInvoiceCreate, CustomerInvoiceUpdate](
    CustomerInvoice
)


@router.post("/", response_model=CustomerInvoiceOut)
def create_invoice(
    invoice_in: CustomerInvoiceCreate,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    return invoice_crud.create(db, obj_in=invoice_in, current_user=current_user)


@router.get("/{invoice_id}", response_model=CustomerInvoiceOut)
def get_invoice(invoice_id: int, db: Session = Depends(get_db)):
    return invoice_crud.get(db, invoice_id)


# @router.get("/", response_model=List[CustomerInvoiceOut])
# def list_invoices(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
#     return invoice_crud.get_multi(db, skip=skip, limit=limit)


@router.get("/", response_model=PaginatedCustomerInvoiceOut)
def list_invoices(
    page: int = Query(1, ge=1),
    limit: int = Query(10, ge=1, le=100),
    db: Session = Depends(get_db),
):
    skip = (page - 1) * limit
    invoices, total = invoice_crud.get_multi_paginated(db, skip=skip, limit=limit)
    total_pages = ceil(total / limit)
    return {
        "data": invoices,
        "total": total,
        "totalPages": total_pages,
        "currentPage": page,
    }


@router.put("/{invoice_id}", response_model=CustomerInvoiceOut)
def update_invoice(
    invoice_id: int,
    invoice_in: CustomerInvoiceUpdate,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    db_invoice = invoice_crud.get(db, invoice_id)
    return invoice_crud.update(
        db, db_invoice, obj_in=invoice_in, current_user=current_user
    )


@router.delete("/{invoice_id}", response_model=CustomerInvoiceOut)
def delete_invoice(
    invoice_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    return invoice_crud.remove(db, invoice_id, current_user=current_user)
