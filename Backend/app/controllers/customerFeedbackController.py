from app.controllers.baseController import BaseController
from app.services.customerFeedbackService import CustomerFeedbackService


class CustomerFeedbackController(BaseController):
    """HTTP shaping for customer feedback. No rules — see CustomerFeedbackService."""

    service_class = CustomerFeedbackService
