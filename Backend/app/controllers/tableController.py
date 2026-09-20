from app.controllers.baseController import BaseController
from app.services.tableService import TableService


class TableController(BaseController):
    """HTTP shaping for table. No rules — see TableService."""

    service_class = TableService
