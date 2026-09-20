from app.controllers.baseController import BaseController
from app.services.salaryStructureService import SalaryStructureService


class SalaryStructureController(BaseController):
    """HTTP shaping for salary structure. No rules — see SalaryStructureService."""

    service_class = SalaryStructureService
