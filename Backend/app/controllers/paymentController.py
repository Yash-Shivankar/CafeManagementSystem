from app.controllers.baseController import BaseController
from app.services.paymentService import PaymentService


class PaymentController(BaseController):
    """HTTP shaping for payment. No rules — see PaymentService."""

    service_class = PaymentService
