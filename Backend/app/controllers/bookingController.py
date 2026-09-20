from app.controllers.baseController import BaseController
from app.services.bookingService import BookingService


class BookingController(BaseController):
    """HTTP shaping for booking. No rules — see BookingService."""

    service_class = BookingService
