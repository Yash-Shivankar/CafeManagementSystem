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
from app.models.Enums import PaymentMethod


class Payment(Common):
    __tablename__ = "payments"

    id = Column(Integer, primary_key=True, index=True)

    invoice_id = Column(
        Integer,
        ForeignKey("customer_invoices.id"),
        nullable=False,
    )

    amount = Column(Numeric(10, 2), nullable=False)

    payment_date = Column(
        DateTime,
        server_default=func.now(),
        nullable=False,
    )

    method = Column(
        SQLEnum(PaymentMethod, name="payment_method_enum"),
        nullable=False,
    )

    invoice = relationship(
        "CustomerInvoice",
        foreign_keys=[invoice_id],
        back_populates="payments",
    )

    def __repr__(self):
        return f"<Payment invoice={self.invoice_id} amount={self.amount}>"
