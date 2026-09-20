from app.controllers.baseController import BaseController
from app.services.employeePerformanceService import EmployeePerformanceService


class EmployeePerformanceController(BaseController):
    """HTTP shaping for performance review. No rules — see EmployeePerformanceService."""

    service_class = EmployeePerformanceService
