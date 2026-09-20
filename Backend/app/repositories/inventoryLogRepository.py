from app.models.InventoryLogs import InventoryLog
from app.repositories.baseRepository import BaseRepository


class InventoryLogRepository(BaseRepository[InventoryLog]):
    """Every inventory log query lives here."""

    model = InventoryLog
    default_relationships = ("item",)
    order_by_column = "changed_on"
    filter_map = {
        "item_id": ("item_id", "eq"),
        "change_type": ("change_type", "eq"),
    }
