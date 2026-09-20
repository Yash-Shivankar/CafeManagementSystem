from app.models.MenuCategory import MenuCategory
from app.repositories.baseRepository import BaseRepository


class MenuCategoryRepository(BaseRepository[MenuCategory]):
    """Menu section queries."""

    model = MenuCategory
    search_columns = ("name", "description")
    filter_map = {
        "is_active": ("is_active", "eq"),
    }
    outlet_shared_when_null = True
    unique_within_outlet = True
    order_by_column = "sort_order"
