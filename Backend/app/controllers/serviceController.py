from app.controllers.baseController import BaseController
from app.services.serviceService import ServiceService


class ServiceController(BaseController):
    """HTTP shaping for service. No rules — see ServiceService."""

    service_class = ServiceService
