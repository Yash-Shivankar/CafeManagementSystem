from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict

from app.models.Enums import PaymentMethod
from app.schemas.customer_invoice import CustomerInvoiceOut


class PaymentBase(BaseModel):
    invoice_id: int
    amount: Decimal
    method: PaymentMethod
    payment_date: datetime | None = None


class PaymentCreate(PaymentBase):
    pass


class PaymentUpdate(BaseModel):
    amount: Decimal | None = None
    method: PaymentMethod | None = None
    payment_date: datetime | None = None


class PaymentOut(BaseModel):
    id: int
    invoice: CustomerInvoiceOut | None
    amount: Decimal
    method: PaymentMethod
    payment_date: datetime | None = None
    created_at: datetime
    updated_at: datetime
    created_by: int | None = None
    updated_by: int | None = None

    model_config = ConfigDict(from_attributes=True)


class PaginatedPaymentOut(BaseModel):
    data: list[PaymentOut]
    total: int
    totalPages: int
    currentPage: int
