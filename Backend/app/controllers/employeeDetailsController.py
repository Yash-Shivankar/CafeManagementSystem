from app.controllers.baseController import BaseController
from app.services.employeeDetailsService import EmployeeDetailsService


class EmployeeDetailsController(BaseController):
    """HTTP shaping for employee. No rules — see EmployeeDetailsService."""

    service_class = EmployeeDetailsService
