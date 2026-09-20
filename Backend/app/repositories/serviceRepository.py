from app.models.Service import Service
from app.repositories.baseRepository import BaseRepository


class ServiceRepository(BaseRepository[Service]):
    """Every service query lives here."""

    model = Service
    outlet_shared_when_null = True
    search_columns = ("name",)
    search_cast_columns = ("price",)
