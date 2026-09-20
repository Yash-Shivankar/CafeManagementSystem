from app.models.Booking import Booking
from app.repositories.baseRepository import BaseRepository


class BookingRepository(BaseRepository[Booking]):
    """Every booking query lives here."""

    model = Booking
