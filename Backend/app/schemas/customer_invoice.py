# app/schemas/customer_invoice.py
from datetime import datetime
from decimal import Decimal
from typing import Optional, Annotated, List
from pydantic import BaseModel, Field
from app.models.Enums import InvoiceStatus
from app.schemas.payment import PaymentOut  # if you want nested payments


class CustomerInvoiceBase(BaseModel):
    user_id: int
    total_amount: Decimal
    paid_amount: Optional[Decimal] = 0
    status: Optional[InvoiceStatus] = InvoiceStatus.UNPAID
    invoice_date: Optional[datetime] = None


class CustomerInvoiceCreate(CustomerInvoiceBase):
    pass


class CustomerInvoiceUpdate(BaseModel):
    total_amount: Optional[Decimal] = None
    paid_amount: Optional[Decimal] = None
    status: Optional[InvoiceStatus] = None
    invoice_date: Optional[datetime] = None


class CustomerInvoiceOut(CustomerInvoiceBase):
    id: int
    created_at: datetime
    updated_at: datetime
    created_by: Optional[int] = None
    updated_by: Optional[int] = None
    deleted_at: Optional[datetime] = None
    is_deleted: Optional[bool] = False
    payments: Optional[List[PaymentOut]] = []

    class Config:
        from_attributes = True
