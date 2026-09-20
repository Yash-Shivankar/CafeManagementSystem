from app.controllers.baseController import BaseController
from app.services.designationService import DesignationService


class DesignationController(BaseController):
    """HTTP shaping for designation. No rules — see DesignationService."""

    service_class = DesignationService
