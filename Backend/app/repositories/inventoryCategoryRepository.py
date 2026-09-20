from app.models.InventoryCategory import InventoryCategory
from app.repositories.baseRepository import BaseRepository


class InventoryCategoryRepository(BaseRepository[InventoryCategory]):
    """Every inventory category query lives here."""

    model = InventoryCategory
    search_columns = ("category_name",)
