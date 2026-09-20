from sqlalchemy import func

from app.models.InventoryItem import InventoryItem
from app.repositories.baseRepository import BaseRepository


class InventoryItemRepository(BaseRepository[InventoryItem]):
    """Every inventory item query lives here."""

    model = InventoryItem
    default_relationships = ("category",)
    search_columns = ("name",)
    filter_map = {
        "category_id": ("category_id", "eq"),
    }

    def _low_stock_query(self, filters=None):
        """At or below the reorder level.

        `<=` rather than `<` on purpose: an item sitting exactly on its minimum
        is the moment to reorder, not one unit later.
        """
        query = self._base_query().filter(
            InventoryItem.quantity <= InventoryItem.min_quantity,
            InventoryItem.min_quantity > 0,
        )
        for condition in filters or []:
            query = query.filter(condition)
        return query

    def low_stock(self, skip: int = 0, limit: int = 10, filters=None):
        query = self._low_stock_query(filters)
        total = query.order_by(None).with_entities(func.count(InventoryItem.id)).scalar() or 0
        rows = (
            query.order_by(
                (InventoryItem.quantity - InventoryItem.min_quantity).asc(),
                InventoryItem.name.asc(),
            )
            .offset(skip)
            .limit(limit)
            .all()
        )
        return rows, total

    def low_stock_count(self, filters=None) -> int:
        return (
            self._low_stock_query(filters).with_entities(func.count(InventoryItem.id)).scalar() or 0
        )
