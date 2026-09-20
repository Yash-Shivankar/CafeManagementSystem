from app.controllers.baseController import BaseController
from app.services.employeeDocumentService import EmployeeDocumentService


class EmployeeDocumentController(BaseController):
    """HTTP shaping for document. No rules — see EmployeeDocumentService."""

    service_class = EmployeeDocumentService
