from app.models.Outlet import Outlet
from app.repositories.baseRepository import BaseRepository


class OutletRepository(BaseRepository[Outlet]):
    """Every outlet query lives here.

    An outlet is not itself outlet-scoped — it *is* the scope — so there is no
    `outlet_id` column and `is_outlet_scoped()` is False. Which outlets a given
    user may see is decided in OutletService, not here.
    """

    model = Outlet
    search_columns = ("name", "code", "city", "state", "gstin")
    order_by_column = "name"
    filter_map = {
        "is_active": ("is_active", "eq"),
        "city": ("city", "eq"),
        "state": ("state", "eq"),
    }
