from app.models.IncrementHistory import IncrementHistory
from app.repositories.baseRepository import BaseRepository


class IncrementHistoryRepository(BaseRepository[IncrementHistory]):
    """Every increment record query lives here."""

    model = IncrementHistory
    outlet_path = "employee"
