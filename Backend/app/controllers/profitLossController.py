from app.controllers.baseController import BaseController
from app.services.profitLossService import ProfitLossService


class ProfitLossController(BaseController):
    """HTTP shaping for profit & loss entry. No rules — see ProfitLossService."""

    service_class = ProfitLossService
    service: ProfitLossService

    def close_day(self, day, expenses):
        return self.service.close_day(day, expenses)
