"""Order and KOT contracts.

Note what is *not* here: no totals on the way in. An order's money is derived
from its lines by `OrderService`, and letting a client send a total is exactly
the anti-pattern that was removed from invoices, payroll and P&L.
"""

from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field, model_validator

from app.models.Enums import OrderItemStatus, OrderStatus, OrderType


class _In(BaseModel):
    """Request bodies.

    `extra="forbid"`: a field the server does not expect is a field the client
    should be told about, not one silently dropped. Dropping one silently is
    how `role_id` on /auth/register became a privilege escalation.
    """

    model_config = ConfigDict(extra="forbid")


class _Out(BaseModel):
    """Responses.

    Deliberately NOT `extra="forbid"`: forbidding extras on the way *out* means
    every audit column the ORM object carries has to be listed or the response
    fails validation with a 500. Input strictness protects the server; output
    strictness only breaks it.
    """

    model_config = ConfigDict(from_attributes=True)


class OrderItemCreate(_In):
    menu_item_id: int
    quantity: Decimal = Field(default=Decimal("1"), gt=0, max_digits=10, decimal_places=3)
    notes: str | None = Field(default=None, max_length=255)


class OrderItemUpdate(_In):
    quantity: Decimal | None = Field(default=None, gt=0, max_digits=10, decimal_places=3)
    notes: str | None = Field(default=None, max_length=255)


class OrderItemStatusUpdate(_In):
    status: OrderItemStatus
    reason: str | None = Field(default=None, max_length=255)

    @model_validator(mode="after")
    def _reason_required_to_void(self):
        if self.status == OrderItemStatus.CANCELLED and not (self.reason or "").strip():
            raise ValueError("Say why the item is being cancelled")
        return self


class OrderItemOut(_Out):
    id: int
    menu_item_id: int | None = None
    item_name: str
    unit_price: Decimal
    tax_rate: Decimal
    hsn_code: str | None = None
    quantity: Decimal
    status: OrderItemStatus
    notes: str | None = None
    void_reason: str | None = None
    fired_at: datetime | None = None
    ready_at: datetime | None = None
    served_at: datetime | None = None


class OrderCreate(_In):
    order_type: OrderType = OrderType.DINE_IN
    table_id: int | None = None
    customer_id: int | None = None
    guest_count: int | None = Field(default=None, ge=1, le=200)
    discount_amount: Decimal = Field(default=Decimal("0"), ge=0, max_digits=10, decimal_places=2)
    service_charge_percent: Decimal = Field(
        default=Decimal("0"), ge=0, le=100, max_digits=5, decimal_places=2
    )
    notes: str | None = Field(default=None, max_length=255)
    items: list[OrderItemCreate] = Field(default_factory=list)


class OrderUpdate(_In):
    table_id: int | None = None
    customer_id: int | None = None
    guest_count: int | None = Field(default=None, ge=1, le=200)
    discount_amount: Decimal | None = Field(default=None, ge=0, max_digits=10, decimal_places=2)
    service_charge_percent: Decimal | None = Field(
        default=None, ge=0, le=100, max_digits=5, decimal_places=2
    )
    notes: str | None = Field(default=None, max_length=255)


class OrderCancel(_In):
    reason: str = Field(min_length=3, max_length=255)


class OrderBillRequest(_In):
    """Raise the bill.

    Everything here is optional and overrides what the order already carries,
    so the till can apply a discount at settlement without having had to guess
    at it when the order was taken.
    """

    discount_amount: Decimal | None = Field(default=None, ge=0, max_digits=10, decimal_places=2)
    service_charge_percent: Decimal | None = Field(
        default=None, ge=0, le=100, max_digits=5, decimal_places=2
    )
    prices_include_tax: bool | None = None
    round_total: bool = True


class OrderTotals(_Out):
    """What the bill would come to, without committing to it.

    Exists so the till can show a running total on the order screen. Computed
    by the same function that produces the real bill, so the preview and the
    printed bill cannot drift apart.
    """

    subtotal: Decimal
    discount_amount: Decimal
    service_charge: Decimal
    taxable_amount: Decimal
    cgst_amount: Decimal
    sgst_amount: Decimal
    tax_amount: Decimal
    round_off: Decimal
    grand_total: Decimal
    tax_breakup: dict[str, dict[str, Decimal]] = Field(default_factory=dict)


class OrderOut(_Out):
    id: int
    outlet_id: int
    order_number: str
    order_type: OrderType
    status: OrderStatus
    table_id: int | None = None
    customer_id: int | None = None
    guest_count: int | None = None
    discount_amount: Decimal
    service_charge_percent: Decimal
    notes: str | None = None
    cancel_reason: str | None = None
    placed_at: datetime
    confirmed_at: datetime | None = None
    closed_at: datetime | None = None
    items: list[OrderItemOut] = Field(default_factory=list)
    created_at: datetime
    updated_at: datetime


class OrderWithTotals(OrderOut):
    totals: OrderTotals


class PaginatedOrderOut(BaseModel):
    data: list[OrderOut]
    total: int
    totalPages: int
    currentPage: int


class KotTicket(_Out):
    """One line on the kitchen display, with the context the pass needs."""

    order_item_id: int
    order_id: int
    order_number: str
    order_type: OrderType
    table_number: str | None = None
    item_name: str
    quantity: Decimal
    notes: str | None = None
    status: OrderItemStatus
    prep_minutes: int | None = None
    fired_at: datetime | None = None
    waiting_seconds: int | None = None


class KotBoard(BaseModel):
    """The queue, oldest first."""

    tickets: list[KotTicket]
    total: int
