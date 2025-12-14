from sqlalchemy import (
    Column,
    Integer,
    Numeric,
    DateTime,
    ForeignKey,
    Enum as SQLEnum,
    func,
)
from sqlalchemy.orm import relationship
from app.models.Common import Common
from app.models.Enums import InvoiceStatus


class CustomerInvoice(Common):
    __tablename__ = "customer_invoices"

    id = Column(Integer, primary_key=True, index=True)

    user_id = Column(
        Integer,
        ForeignKey("users.id"),
        nullable=False,
    )

    total_amount = Column(Numeric(10, 2), nullable=False)
    paid_amount = Column(Numeric(10, 2), default=0)

    status = Column(
        SQLEnum(InvoiceStatus, name="invoice_status_enum"),
        nullable=False,
        default=InvoiceStatus.UNPAID,
    )

    invoice_date = Column(
        DateTime,
        server_default=func.now(),
        nullable=False,
    )

    user = relationship(
        "User",
        foreign_keys=[user_id],
        back_populates="invoices",
    )

    payments = relationship(
        "Payment",
        foreign_keys="Payment.invoice_id",
        back_populates="invoice",
        cascade="all, delete-orphan",
    )

    def __repr__(self):
        return f"<Invoice id={self.id} status={self.status}>"
