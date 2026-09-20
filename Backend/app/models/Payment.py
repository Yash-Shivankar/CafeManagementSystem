from sqlalchemy import (
    Column,
    DateTime,
    ForeignKey,
    Index,
    Integer,
    Numeric,
    func,
)
from sqlalchemy import (
    Enum as SQLEnum,
)
from sqlalchemy.orm import relationship

from app.models.Common import Common
from app.models.Enums import PaymentMethod, enum_values


class Payment(Common):
    __tablename__ = "payments"
    __table_args__ = (Index("ix_payments_outlet_deleted", "outlet_id", "is_deleted"),)

    id = Column(Integer, primary_key=True, index=True)
    outlet_id = Column(
        Integer,
        ForeignKey("outlets.id"),
        nullable=False,
        index=True,
    )

    invoice_id = Column(
        Integer,
        ForeignKey("customer_invoices.id"),
        nullable=False,
    )

    amount = Column(Numeric(10, 2), nullable=False)

    payment_date = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

    method = Column(
        SQLEnum(PaymentMethod, name="payment_method_enum", values_callable=enum_values),
        nullable=False,
    )

    invoice = relationship(
        "CustomerInvoice",
        foreign_keys=[invoice_id],
        back_populates="payments",
    )

    outlet = relationship("Outlet", foreign_keys=[outlet_id])

    def __repr__(self):
        return f"<Payment invoice={self.invoice_id} amount={self.amount}>"
