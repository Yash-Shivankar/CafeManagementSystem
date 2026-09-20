from app.controllers.baseController import BaseController
from app.services.incentiveService import IncentiveService


class IncentiveController(BaseController):
    """HTTP shaping for incentive. No rules — see IncentiveService."""

    service_class = IncentiveService
