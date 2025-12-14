from sqlalchemy import (
    Column,
    Integer,
    String,
    Numeric,
    ForeignKey,
)
from sqlalchemy.orm import relationship
from app.models.Common import Common


class InventoryItem(Common):
    __tablename__ = "inventory_items"

    id = Column(Integer, primary_key=True, index=True)

    name = Column(String(100), nullable=False, index=True)

    category_id = Column(
        Integer,
        ForeignKey("inventory_categories.id"),
        nullable=False,
    )

    quantity = Column(Integer, nullable=False, default=0)

    cost_price = Column(Numeric(10, 2), nullable=False)
    selling_price = Column(Numeric(10, 2), nullable=False)

    min_quantity = Column(Integer, nullable=False, default=0)

    category = relationship(
        "InventoryCategory",
        foreign_keys=[category_id],
        back_populates="items",
    )

    logs = relationship(
        "InventoryLog",
        foreign_keys="InventoryLog.item_id",
        back_populates="item",
    )

    def __repr__(self):
        return f"<InventoryItem {self.name} qty={self.quantity}>"
