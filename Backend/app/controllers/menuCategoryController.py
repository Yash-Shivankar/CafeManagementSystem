from app.controllers.baseController import BaseController
from app.services.menuCategoryService import MenuCategoryService


class MenuCategoryController(BaseController):
    """HTTP shaping for menu sections. No rules — see MenuCategoryService."""

    service_class = MenuCategoryService
