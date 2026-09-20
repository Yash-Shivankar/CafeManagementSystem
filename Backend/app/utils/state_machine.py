"""Status transitions, declared rather than assumed.

Every status column in this system was a free-for-all: a settled invoice could
be set back to `unpaid`, a cancelled booking could be marked `completed`, and a
terminated employee could be flipped to `active` with no record of it. Nothing
in the code said which moves were legal, so every move was.

A transition table is the smallest thing that fixes that, and it reads as
documentation: you can see the whole lifecycle of an invoice in six lines.
"""

from __future__ import annotations

from app.models.Enums import (
    BookingStatus,
    EmployeeStatus,
    InvoiceStatus,
    OrderItemStatus,
    OrderStatus,
)
from app.utils.exceptions import BusinessRuleError


class StateMachine:
    """A set of allowed `from -> to` moves for one status column."""

    def __init__(self, name: str, transitions: dict, terminal: set | None = None):
        self.name = name
        self.transitions = transitions
        self.terminal = terminal or set()

    def can(self, current, target) -> bool:
        if current == target:
            return True
        return target in self.transitions.get(current, set())

    def assert_can(self, current, target) -> None:
        if self.can(current, target):
            return

        current_label = getattr(current, "value", current)
        target_label = getattr(target, "value", target)

        if current in self.terminal:
            raise BusinessRuleError(
                f"{self.name} is {current_label}, which is final. It cannot become {target_label}."
            )

        allowed = sorted(getattr(s, "value", s) for s in self.transitions.get(current, set()))
        raise BusinessRuleError(
            f"{self.name} cannot go from {current_label} to {target_label}."
            + (f" Allowed from here: {', '.join(allowed)}." if allowed else "")
        )


INVOICE_STATUS = StateMachine(
    "Invoice",
    {
        InvoiceStatus.UNPAID: {InvoiceStatus.PARTIAL, InvoiceStatus.PAID},
        InvoiceStatus.PARTIAL: {InvoiceStatus.PAID, InvoiceStatus.UNPAID},
        InvoiceStatus.PAID: set(),
    },
    terminal={InvoiceStatus.PAID},
)

BOOKING_STATUS = StateMachine(
    "Booking",
    {
        BookingStatus.SCHEDULED: {
            BookingStatus.COMPLETED,
            BookingStatus.CANCELLED,
        },
        BookingStatus.COMPLETED: set(),
        BookingStatus.CANCELLED: set(),
    },
    terminal={BookingStatus.COMPLETED, BookingStatus.CANCELLED},
)

EMPLOYEE_STATUS = StateMachine(
    "Employee",
    {
        EmployeeStatus.ACTIVE: {
            EmployeeStatus.INACTIVE,
            EmployeeStatus.RESIGNED,
            EmployeeStatus.TERMINATED,
        },
        EmployeeStatus.INACTIVE: {
            EmployeeStatus.ACTIVE,
            EmployeeStatus.RESIGNED,
            EmployeeStatus.TERMINATED,
        },
        EmployeeStatus.RESIGNED: set(),
        EmployeeStatus.TERMINATED: set(),
    },
    terminal={EmployeeStatus.RESIGNED, EmployeeStatus.TERMINATED},
)


ORDER_STATUS = StateMachine(
    "Order",
    {
        OrderStatus.OPEN: {OrderStatus.CONFIRMED, OrderStatus.CANCELLED},
        OrderStatus.CONFIRMED: {
            OrderStatus.SERVED,
            OrderStatus.BILLED,
            OrderStatus.CANCELLED,
        },
        OrderStatus.SERVED: {OrderStatus.BILLED, OrderStatus.CANCELLED},
        OrderStatus.BILLED: set(),
        OrderStatus.CANCELLED: set(),
    },
    terminal={OrderStatus.BILLED, OrderStatus.CANCELLED},
)

ORDER_ITEM_STATUS = StateMachine(
    "Order item",
    {
        OrderItemStatus.PENDING: {OrderItemStatus.FIRED, OrderItemStatus.CANCELLED},
        OrderItemStatus.FIRED: {
            OrderItemStatus.READY,
            OrderItemStatus.SERVED,
            OrderItemStatus.CANCELLED,
        },
        OrderItemStatus.READY: {OrderItemStatus.SERVED, OrderItemStatus.CANCELLED},
        OrderItemStatus.SERVED: set(),
        OrderItemStatus.CANCELLED: set(),
    },
    terminal={OrderItemStatus.SERVED, OrderItemStatus.CANCELLED},
)
