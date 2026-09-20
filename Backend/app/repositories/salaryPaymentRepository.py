from app.models.SalaryPayment import SalaryPayment
from app.repositories.baseRepository import BaseRepository


class SalaryPaymentRepository(BaseRepository[SalaryPayment]):
    """Every salary payment query lives here."""

    model = SalaryPayment
