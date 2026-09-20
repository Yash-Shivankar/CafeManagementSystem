from app.controllers.baseController import BaseController
from app.services.inventoryItemService import InventoryItemService


class InventoryItemController(BaseController):
    """HTTP shaping for inventory item. No rules — see InventoryItemService."""

    service_class = InventoryItemService
    service: InventoryItemService

    def low_stock(self, params):
        from app.utils.pagination import paginate

        rows, total = self.service.low_stock(params)
        return paginate(rows, total, params)
