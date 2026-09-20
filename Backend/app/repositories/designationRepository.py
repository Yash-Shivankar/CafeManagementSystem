from app.models.Designation import Designation
from app.repositories.baseRepository import BaseRepository


class DesignationRepository(BaseRepository[Designation]):
    """Every designation query lives here."""

    model = Designation
    search_columns = ("designation_name",)
