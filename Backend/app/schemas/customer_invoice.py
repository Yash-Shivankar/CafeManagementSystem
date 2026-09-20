from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field

from app.models.Enums import InvoiceStatus
from app.schemas.user import UserOut


class CustomerInvoiceBase(BaseModel):
    user_id: int
    total_amount: Decimal
    paid_amount: Decimal | None = Decimal("0")
    status: InvoiceStatus | None = InvoiceStatus.UNPAID
    invoice_date: datetime | None = None


class CustomerInvoiceCreate(CustomerInvoiceBase):
    """A bill raised by hand.

    Still supported — a cafe sells a gift card or charges for a private
    booking, and neither is an order. A bill that came from an order is raised
    by `POST /orders/{id}/bill`, which is the path that carries line items and
    a tax breakup.
    """


class CustomerInvoiceUpdate(BaseModel):
    total_amount: Decimal | None = None
    paid_amount: Decimal | None = None
    status: InvoiceStatus | None = None
    invoice_date: datetime | None = None


class InvoiceLineOut(BaseModel):
    """One printed line. Written once by OrderService.bill() and never edited —
    a wrong bill is corrected with a credit note, not by rewriting history."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    description: str
    hsn_code: str | None = None
    quantity: Decimal
    unit_price: Decimal
    discount_amount: Decimal
    tax_rate: Decimal
    taxable_amount: Decimal
    cgst_amount: Decimal
    sgst_amount: Decimal
    line_total: Decimal


class CustomerInvoiceOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    user: UserOut | None = None
    order_id: int | None = None
    invoice_number: str | None = None

    subtotal: Decimal = Decimal("0")
    discount_amount: Decimal = Decimal("0")
    service_charge: Decimal = Decimal("0")
    taxable_amount: Decimal = Decimal("0")
    cgst_amount: Decimal = Decimal("0")
    sgst_amount: Decimal = Decimal("0")
    tax_amount: Decimal = Decimal("0")
    round_off: Decimal = Decimal("0")

    total_amount: Decimal
    paid_amount: Decimal | None = Decimal("0")
    status: InvoiceStatus | None = InvoiceStatus.UNPAID

    is_void: bool = False
    void_reason: str | None = None

    lines: list[InvoiceLineOut] = Field(default_factory=list)

    invoice_date: datetime | None = None
    created_at: datetime
    updated_at: datetime
    created_by: int | None = None
    updated_by: int | None = None


class PaginatedCustomerInvoiceOut(BaseModel):
    data: list[CustomerInvoiceOut]
    total: int
    totalPages: int
    currentPage: int
