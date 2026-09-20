from app.controllers.baseController import BaseController
from app.services.inventoryCategoryService import InventoryCategoryService


class InventoryCategoryController(BaseController):
    """HTTP shaping for inventory category. No rules — see InventoryCategoryService."""

    service_class = InventoryCategoryService
