from sqlalchemy import (
    Column,
    DateTime,
    ForeignKey,
    Index,
    Integer,
    Numeric,
    String,
)
from sqlalchemy import (
    Enum as SQLEnum,
)
from sqlalchemy.orm import relationship

from app.models.Common import Common
from app.models.Enums import OrderItemStatus, enum_values


class OrderItem(Common):
    """One line of an order, and one ticket on the kitchen display.

    Everything the bill needs is **snapshotted** here — name, price, tax rate —
    rather than read through `menu_item` at bill time. A menu item's price
    changes; a line that was sold at 180 was sold at 180 forever. Reading it
    live is the bug where last month's revenue quietly moves when someone
    edits the menu.
    """

    __tablename__ = "order_items"
    __table_args__ = (
        Index("ix_order_items_order", "order_id", "is_deleted"),
        Index("ix_order_items_status", "status", "is_deleted"),
    )

    id = Column(Integer, primary_key=True, index=True)
    order_id = Column(Integer, ForeignKey("orders.id"), nullable=False, index=True)

    menu_item_id = Column(Integer, ForeignKey("menu_items.id"), nullable=True, index=True)

    item_name = Column(String(120), nullable=False)
    unit_price = Column(Numeric(10, 2), nullable=False)
    tax_rate = Column(Numeric(5, 2), nullable=False, default=5)
    hsn_code = Column(String(12), nullable=True)

    quantity = Column(Numeric(10, 3), nullable=False, default=1)

    status = Column(
        SQLEnum(OrderItemStatus, name="order_item_status_enum", values_callable=enum_values),
        nullable=False,
        default=OrderItemStatus.PENDING,
    )

    notes = Column(String(255), nullable=True)

    void_reason = Column(String(255), nullable=True)

    fired_at = Column(DateTime(timezone=True), nullable=True)
    ready_at = Column(DateTime(timezone=True), nullable=True)
    served_at = Column(DateTime(timezone=True), nullable=True)

    order = relationship("Order", foreign_keys=[order_id], back_populates="items")
    menu_item = relationship(
        "MenuItem",
        foreign_keys=[menu_item_id],
        back_populates="order_items",
    )

    def __repr__(self):
        return f"<OrderItem {self.item_name} x{self.quantity} {self.status}>"
