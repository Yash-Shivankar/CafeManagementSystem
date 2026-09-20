from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    ForeignKey,
    Index,
    Integer,
    Numeric,
    String,
    UniqueConstraint,
    func,
)
from sqlalchemy import (
    Enum as SQLEnum,
)
from sqlalchemy.orm import relationship

from app.models.Common import Common
from app.models.Enums import InvoiceStatus, enum_values


class CustomerInvoice(Common):
    """A bill.

    Everything below `total_amount` exists so a bill can be reprinted, checked
    and reported on. A single hand-typed figure with no line items, no tax
    breakup and no link to what was actually sold is none of those things. An
    invoice is derived from an order by `OrderService.bill()`, and every
    component of the total is stored beside it.

    `total_amount` and `paid_amount` keep their old meaning so nothing that
    already reads them breaks: total is what is owed, paid is the sum of the
    payments recorded (CustomerInvoiceService.settle owns both).
    """

    __tablename__ = "customer_invoices"
    __table_args__ = (
        UniqueConstraint("outlet_id", "invoice_number", name="uq_customer_invoices_number"),
        Index("ix_customer_invoices_outlet_deleted", "outlet_id", "is_deleted"),
        Index("ix_customer_invoices_date", "outlet_id", "invoice_date"),
    )

    id = Column(Integer, primary_key=True, index=True)
    outlet_id = Column(
        Integer,
        ForeignKey("outlets.id"),
        nullable=False,
        index=True,
    )

    user_id = Column(
        Integer,
        ForeignKey("users.id"),
        nullable=False,
    )

    order_id = Column(Integer, ForeignKey("orders.id"), nullable=True, index=True)

    invoice_number = Column(String(32), nullable=True)

    subtotal = Column(Numeric(10, 2), nullable=False, default=0)
    discount_amount = Column(Numeric(10, 2), nullable=False, default=0)
    service_charge = Column(Numeric(10, 2), nullable=False, default=0)
    taxable_amount = Column(Numeric(10, 2), nullable=False, default=0)
    cgst_amount = Column(Numeric(10, 2), nullable=False, default=0)
    sgst_amount = Column(Numeric(10, 2), nullable=False, default=0)
    tax_amount = Column(Numeric(10, 2), nullable=False, default=0)
    round_off = Column(Numeric(10, 2), nullable=False, default=0)

    total_amount = Column(Numeric(10, 2), nullable=False)
    paid_amount = Column(Numeric(10, 2), default=0)

    status = Column(
        SQLEnum(InvoiceStatus, name="invoice_status_enum", values_callable=enum_values),
        nullable=False,
        default=InvoiceStatus.UNPAID,
    )

    is_void = Column(Boolean, nullable=False, default=False)
    void_reason = Column(String(255), nullable=True)

    invoice_date = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

    user = relationship(
        "User",
        foreign_keys=[user_id],
        back_populates="invoices",
    )

    order = relationship(
        "Order",
        foreign_keys=[order_id],
        back_populates="invoice",
    )

    lines = relationship(
        "InvoiceLine",
        foreign_keys="InvoiceLine.invoice_id",
        back_populates="invoice",
        cascade="all, delete-orphan",
    )

    payments = relationship(
        "Payment",
        foreign_keys="Payment.invoice_id",
        back_populates="invoice",
        cascade="all, delete-orphan",
    )

    outlet = relationship("Outlet", foreign_keys=[outlet_id])

    def __repr__(self):
        return f"<Invoice id={self.id} status={self.status}>"
