from app.controllers.baseController import BaseController
from app.services.incrementHistoryService import IncrementHistoryService


class IncrementHistoryController(BaseController):
    """HTTP shaping for increment record. No rules — see IncrementHistoryService."""

    service_class = IncrementHistoryService
