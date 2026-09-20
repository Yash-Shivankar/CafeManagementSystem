from app.controllers.baseController import BaseController
from app.services.departmentService import DepartmentService


class DepartmentController(BaseController):
    """HTTP shaping for department. No rules — see DepartmentService."""

    service_class = DepartmentService
