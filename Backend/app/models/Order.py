from sqlalchemy import (
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
from app.models.Enums import OrderStatus, OrderType, enum_values


class Order(Common):
    """A customer's order — the spine the rest of the POS hangs off.

    An order is *not* a bill. It is what the kitchen and the floor work from;
    the bill is derived from it once, at the end, by `OrderService.bill()`.
    Keeping them apart is what lets an order be edited while it is open and
    frozen the moment money is involved.
    """

    __tablename__ = "orders"
    __table_args__ = (
        UniqueConstraint("outlet_id", "order_number", name="uq_orders_outlet_number"),
        Index("ix_orders_outlet_deleted", "outlet_id", "is_deleted"),
        Index("ix_orders_outlet_status", "outlet_id", "status", "is_deleted"),
        Index("ix_orders_placed_at", "outlet_id", "placed_at"),
    )

    id = Column(Integer, primary_key=True, index=True)
    outlet_id = Column(Integer, ForeignKey("outlets.id"), nullable=False, index=True)

    order_number = Column(String(24), nullable=False)

    order_type = Column(
        SQLEnum(OrderType, name="order_type_enum", values_callable=enum_values),
        nullable=False,
        default=OrderType.DINE_IN,
    )

    status = Column(
        SQLEnum(OrderStatus, name="order_status_enum", values_callable=enum_values),
        nullable=False,
        default=OrderStatus.OPEN,
    )

    table_id = Column(Integer, ForeignKey("tables.id"), nullable=True, index=True)

    customer_id = Column(Integer, ForeignKey("users.id"), nullable=True)

    guest_count = Column(Integer, nullable=True)

    discount_amount = Column(Numeric(10, 2), nullable=False, default=0)
    service_charge_percent = Column(Numeric(5, 2), nullable=False, default=0)

    notes = Column(String(255), nullable=True)

    cancel_reason = Column(String(255), nullable=True)

    placed_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    confirmed_at = Column(DateTime(timezone=True), nullable=True)
    closed_at = Column(DateTime(timezone=True), nullable=True)

    items = relationship(
        "OrderItem",
        foreign_keys="OrderItem.order_id",
        back_populates="order",
        cascade="all, delete-orphan",
    )

    invoice = relationship(
        "CustomerInvoice",
        foreign_keys="CustomerInvoice.order_id",
        back_populates="order",
        uselist=False,
    )

    table = relationship("Table", foreign_keys=[table_id])
    customer = relationship("User", foreign_keys=[customer_id])
    outlet = relationship("Outlet", foreign_keys=[outlet_id])

    def __repr__(self):
        return f"<Order {self.order_number} {self.status}>"
