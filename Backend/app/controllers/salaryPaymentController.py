from app.controllers.baseController import BaseController
from app.services.salaryPaymentService import SalaryPaymentService


class SalaryPaymentController(BaseController):
    """HTTP shaping for salary payment. No rules — see SalaryPaymentService."""

    service_class = SalaryPaymentService
    service: SalaryPaymentService

    def preview(self, employee_id: int, month: str, year: int):
        return self.service.compute(employee_id, month, year)

    def generate(self, employee_id: int, month: str, year: int):
        return self.service.generate(employee_id, month, year)
