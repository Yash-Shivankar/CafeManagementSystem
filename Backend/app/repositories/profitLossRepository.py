from app.models.ProfitLoss import ProfitLoss
from app.repositories.baseRepository import BaseRepository


class ProfitLossRepository(BaseRepository[ProfitLoss]):
    """Every profit & loss query lives here."""

    model = ProfitLoss
    order_by_column = "date"
    filter_map = {
        "start_date": ("date", "gte"),
        "end_date": ("date", "lte"),
    }
