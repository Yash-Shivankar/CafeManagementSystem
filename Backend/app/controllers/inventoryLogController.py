from app.controllers.baseController import BaseController
from app.services.inventoryLogService import InventoryLogService


class InventoryLogController(BaseController):
    """HTTP shaping for inventory logs. No rules — see InventoryLogService."""

    service_class = InventoryLogService
