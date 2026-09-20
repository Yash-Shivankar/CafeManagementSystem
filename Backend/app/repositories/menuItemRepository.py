from app.models.MenuItem import MenuItem
from app.repositories.baseRepository import BaseRepository


class MenuItemRepository(BaseRepository[MenuItem]):
    """Menu item queries."""

    model = MenuItem
    default_relationships = ("category",)
    search_columns = ("name", "description", "hsn_code")
    search_relations = (("category", ("name",)),)
    filter_map = {
        "category_id": ("category_id", "eq"),
        "is_veg": ("is_veg", "eq"),
        "is_available": ("is_available", "eq"),
        "is_active": ("is_active", "eq"),
        "min_price": ("price", "gte"),
        "max_price": ("price", "lte"),
    }
    outlet_shared_when_null = True
    unique_within_outlet = True
    order_by_column = "name"
