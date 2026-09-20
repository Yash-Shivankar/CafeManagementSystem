from sqlalchemy import (
    Column,
    DateTime,
    ForeignKey,
    Index,
    Integer,
    String,
    func,
)
from sqlalchemy import (
    Enum as SQLEnum,
)
from sqlalchemy.orm import relationship

from app.models.Common import Common
from app.models.Enums import InventoryChangeType, enum_values


class InventoryLog(Common):
    __tablename__ = "inventory_logs"
    __table_args__ = (Index("ix_inventory_logs_outlet_deleted", "outlet_id", "is_deleted"),)

    id = Column(Integer, primary_key=True, index=True)
    outlet_id = Column(
        Integer,
        ForeignKey("outlets.id"),
        nullable=False,
        index=True,
    )

    item_id = Column(
        Integer,
        ForeignKey("inventory_items.id"),
        nullable=False,
    )

    change_type = Column(
        SQLEnum(
            InventoryChangeType, name="inventory_change_type_enum", values_callable=enum_values
        ),
        nullable=False,
    )

    quantity = Column(Integer, nullable=False)

    changed_on = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

    reference = Column(String(100), nullable=True)

    item = relationship(
        "InventoryItem",
        foreign_keys=[item_id],
        back_populates="logs",
    )

    outlet = relationship("Outlet", foreign_keys=[outlet_id])

    def __repr__(self):
        return f"<InventoryLog item={self.item_id} {self.change_type} {self.quantity}>"
