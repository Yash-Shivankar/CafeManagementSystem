from app.controllers.baseController import BaseController
from app.services.outletService import OutletService


class OutletController(BaseController):
    """HTTP shaping for outlets. No rules — see OutletService."""

    service_class = OutletService
