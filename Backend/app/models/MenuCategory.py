from sqlalchemy import (
    Boolean,
    Column,
    ForeignKey,
    Index,
    Integer,
    String,
    UniqueConstraint,
)
from sqlalchemy.orm import relationship

from app.models.Common import Common


class MenuCategory(Common):
    """A section of the menu — Hot Coffee, Cold Brew, Bakery.

    `outlet_id` is nullable on purpose. A chain pushes one menu to every branch,
    and a branch adds a few things of its own; NULL means "available at every
    outlet" and the repository's `outlet_shared_when_null` flag is what makes a
    branch see both its own categories and the chain's.
    """

    __tablename__ = "menu_categories"
    __table_args__ = (
        UniqueConstraint("outlet_id", "name", name="uq_menu_categories_outlet_name"),
        Index("ix_menu_categories_outlet_deleted", "outlet_id", "is_deleted"),
    )

    id = Column(Integer, primary_key=True, index=True)
    outlet_id = Column(Integer, ForeignKey("outlets.id"), nullable=True, index=True)

    name = Column(String(80), nullable=False)
    description = Column(String(255), nullable=True)

    sort_order = Column(Integer, nullable=False, default=0)

    is_active = Column(Boolean, nullable=False, default=True)

    items = relationship(
        "MenuItem",
        foreign_keys="MenuItem.category_id",
        back_populates="category",
    )

    outlet = relationship("Outlet", foreign_keys=[outlet_id])

    def __repr__(self):
        return f"<MenuCategory {self.name}>"
