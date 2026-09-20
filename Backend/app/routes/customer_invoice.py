"""CustomerInvoices endpoints.

HTTP binding only: path, verb, response model. What happens next is
CustomerInvoiceService; how it is fetched is CustomerInvoiceRepository.
"""

from datetime import date

from fastapi import APIRouter, Depends, Query

from app.controllers.customerInvoiceController import CustomerInvoiceController
from app.schemas.customer_invoice import (
    CustomerInvoiceCreate,
    CustomerInvoiceOut,
    CustomerInvoiceUpdate,
    PaginatedCustomerInvoiceOut,
)
from app.utils.pagination import PageParams, page_params

router = APIRouter(prefix="/customer-invoices", tags=["CustomerInvoices"])


@router.get("/", response_model=PaginatedCustomerInvoiceOut)
def list_invoices(
    start_date: date | None = Query(None),
    end_date: date | None = Query(None),
    status: str | None = Query(None),
    search: str | None = Query(None, min_length=1),
    params: PageParams = Depends(page_params),
    controller: CustomerInvoiceController = Depends(),
):
    return controller.list(
        params,
        search=search,
        start_date=start_date,
        end_date=end_date,
        status=status,
    )


@router.get("/{invoice_id}", response_model=CustomerInvoiceOut)
def get_invoice(
    invoice_id: int,
    controller: CustomerInvoiceController = Depends(),
):
    return controller.get(invoice_id)


@router.post("/", response_model=CustomerInvoiceOut)
def create_invoice(
    payload: CustomerInvoiceCreate,
    controller: CustomerInvoiceController = Depends(),
):
    return controller.create(payload)


@router.put("/{invoice_id}", response_model=CustomerInvoiceOut)
def update_invoice(
    invoice_id: int,
    payload: CustomerInvoiceUpdate,
    controller: CustomerInvoiceController = Depends(),
):
    return controller.update(invoice_id, payload)


@router.delete("/{invoice_id}", response_model=CustomerInvoiceOut)
def delete_invoice(
    invoice_id: int,
    controller: CustomerInvoiceController = Depends(),
):
    return controller.delete(invoice_id)
