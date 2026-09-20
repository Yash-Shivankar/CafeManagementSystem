from app.controllers.baseController import BaseController
from app.services.customerInvoiceService import CustomerInvoiceService


class CustomerInvoiceController(BaseController):
    """HTTP shaping for invoice. No rules — see CustomerInvoiceService."""

    service_class = CustomerInvoiceService
