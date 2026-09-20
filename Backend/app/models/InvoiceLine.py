from sqlalchemy import (
    Column,
    ForeignKey,
    Index,
    Integer,
    Numeric,
    String,
)
from sqlalchemy.orm import relationship

from app.models.Common import Common


class InvoiceLine(Common):
    """One printed line of a bill.

    Without these rows a `CustomerInvoice` is a hand-typed `total_amount` and
    nothing else, and the system cannot answer *"what sold today?"* — the
    question a cafe owner asks every single evening. These rows are that
    answer, and they are also what a GST return is built from.

    They are written once, by `OrderService.bill()`, and never edited. A wrong
    bill is corrected by a credit note, not by rewriting history — the same
    rule the stock ledger and the audit trail already follow.
    """

    __tablename__ = "invoice_lines"
    __table_args__ = (
        Index("ix_invoice_lines_invoice", "invoice_id", "is_deleted"),
        Index("ix_invoice_lines_menu_item", "menu_item_id"),
    )

    id = Column(Integer, primary_key=True, index=True)
    invoice_id = Column(Integer, ForeignKey("customer_invoices.id"), nullable=False, index=True)

    menu_item_id = Column(Integer, ForeignKey("menu_items.id"), nullable=True)
    order_item_id = Column(Integer, ForeignKey("order_items.id"), nullable=True)

    description = Column(String(160), nullable=False)
    hsn_code = Column(String(12), nullable=True)

    quantity = Column(Numeric(10, 3), nullable=False)
    unit_price = Column(Numeric(10, 2), nullable=False)

    discount_amount = Column(Numeric(10, 2), nullable=False, default=0)

    tax_rate = Column(Numeric(5, 2), nullable=False, default=0)
    taxable_amount = Column(Numeric(10, 2), nullable=False)
    cgst_amount = Column(Numeric(10, 2), nullable=False, default=0)
    sgst_amount = Column(Numeric(10, 2), nullable=False, default=0)
    line_total = Column(Numeric(10, 2), nullable=False)

    invoice = relationship(
        "CustomerInvoice",
        foreign_keys=[invoice_id],
        back_populates="lines",
    )
    menu_item = relationship("MenuItem", foreign_keys=[menu_item_id])

    def __repr__(self):
        return f"<InvoiceLine {self.description} x{self.quantity}>"
