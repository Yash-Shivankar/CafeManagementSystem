# app/schemas/payment.py
from datetime import datetime
from decimal import Decimal
from typing import Optional, Annotated, List
from pydantic import BaseModel, Field
from app.models.Enums import PaymentMethod
from app.schemas.customer_invoice import CustomerInvoiceOut


class PaymentBase(BaseModel):
    invoice_id: int
    amount: Decimal
    method: PaymentMethod
    payment_date: Optional[datetime] = None


class PaymentCreate(PaymentBase):
    pass


class PaymentUpdate(BaseModel):
    amount: Optional[Decimal] = None
    method: Optional[PaymentMethod] = None
    payment_date: Optional[datetime] = None


class PaymentOut(BaseModel):
    id: int
    invoice: Optional[CustomerInvoiceOut]
    amount: Decimal
    method: PaymentMethod
    payment_date: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime
    created_by: Optional[int] = None
    updated_by: Optional[int] = None
    # deleted_at: Optional[datetime] = None
    # is_deleted: Optional[bool] = False

    class Config:
        from_attributes = True


class PaginatedPaymentOut(BaseModel):
    data: List[PaymentOut]
    total: int
    totalPages: int
    currentPage: int
