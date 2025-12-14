from sqlalchemy import (
    Column,
    Integer,
    DateTime,
    String,
    ForeignKey,
    Enum as SQLEnum,
    func,
)
from sqlalchemy.orm import relationship
from app.models.Common import Common
from app.models.Enums import InventoryChangeType


class InventoryLog(Common):
    __tablename__ = "inventory_logs"

    id = Column(Integer, primary_key=True, index=True)

    item_id = Column(
        Integer,
        ForeignKey("inventory_items.id"),
        nullable=False,
    )

    change_type = Column(
        SQLEnum(InventoryChangeType, name="inventory_change_type_enum"),
        nullable=False,
    )

    quantity = Column(Integer, nullable=False)

    changed_on = Column(
        DateTime,
        server_default=func.now(),
        nullable=False,
    )

    reference = Column(String(100), nullable=True)

    item = relationship(
        "InventoryItem",
        foreign_keys=[item_id],
        back_populates="logs",
    )

    def __repr__(self):
        return f"<InventoryLog item={self.item_id} {self.change_type} {self.quantity}>"
