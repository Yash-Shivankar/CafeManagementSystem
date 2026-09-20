from sqlalchemy import (
    Boolean,
    Column,
    ForeignKey,
    Index,
    Integer,
    Numeric,
    String,
    UniqueConstraint,
)
from sqlalchemy.orm import relationship

from app.models.Common import Common


class MenuItem(Common):
    """Something a customer can order.

    The price here is the *current* price. An order line copies it at the
    moment of ordering (see `OrderItem.unit_price`), because a price change
    tonight must not silently rewrite this afternoon's bills — that is the
    difference between a catalogue and a ledger.
    """

    __tablename__ = "menu_items"
    __table_args__ = (
        UniqueConstraint("outlet_id", "name", name="uq_menu_items_outlet_name"),
        Index("ix_menu_items_outlet_deleted", "outlet_id", "is_deleted"),
        Index("ix_menu_items_category", "category_id", "is_deleted"),
    )

    id = Column(Integer, primary_key=True, index=True)
    outlet_id = Column(Integer, ForeignKey("outlets.id"), nullable=True, index=True)
    category_id = Column(Integer, ForeignKey("menu_categories.id"), nullable=False, index=True)

    name = Column(String(120), nullable=False)
    description = Column(String(255), nullable=True)

    price = Column(Numeric(10, 2), nullable=False)

    tax_rate = Column(Numeric(5, 2), nullable=False, default=5)

    hsn_code = Column(String(12), nullable=True)

    is_veg = Column(Boolean, nullable=False, default=True)

    is_available = Column(Boolean, nullable=False, default=True)
    is_active = Column(Boolean, nullable=False, default=True)

    prep_minutes = Column(Integer, nullable=True)

    category = relationship(
        "MenuCategory",
        foreign_keys=[category_id],
        back_populates="items",
    )

    order_items = relationship(
        "OrderItem",
        foreign_keys="OrderItem.menu_item_id",
        back_populates="menu_item",
    )

    outlet = relationship("Outlet", foreign_keys=[outlet_id])

    def __repr__(self):
        return f"<MenuItem {self.name} {self.price}>"
