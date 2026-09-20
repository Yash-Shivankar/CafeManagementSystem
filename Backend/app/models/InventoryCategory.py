from sqlalchemy import Column, Index, Integer, String, UniqueConstraint
from sqlalchemy.orm import relationship

from app.models.Common import Common


class InventoryCategory(Common):
    __tablename__ = "inventory_categories"
    __table_args__ = (
        UniqueConstraint("category_name", name="uq_inventory_category_name"),
        Index("ix_inventory_categories_is_deleted", "is_deleted"),
    )

    id = Column(Integer, primary_key=True, index=True)
    category_name = Column(String(100), nullable=False)

    items = relationship(
        "InventoryItem",
        foreign_keys="InventoryItem.category_id",
        back_populates="category",
    )

    def __repr__(self):
        return f"<InventoryCategory {self.name}>"
