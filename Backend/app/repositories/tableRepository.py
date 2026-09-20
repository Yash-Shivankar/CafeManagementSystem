from app.models.Table import Table
from app.repositories.baseRepository import BaseRepository


class TableRepository(BaseRepository[Table]):
    """Every table query lives here."""

    model = Table
    unique_within_outlet = True
    search_columns = ("table_number",)
    search_cast_columns = ("seating_capacity",)
