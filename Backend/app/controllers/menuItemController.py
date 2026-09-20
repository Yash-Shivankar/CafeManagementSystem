from app.controllers.baseController import BaseController
from app.services.menuItemService import MenuItemService


class MenuItemController(BaseController):
    """HTTP shaping for menu items. No rules — see MenuItemService."""

    service_class = MenuItemService
