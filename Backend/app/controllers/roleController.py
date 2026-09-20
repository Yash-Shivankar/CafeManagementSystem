from app.controllers.baseController import BaseController
from app.services.roleService import RoleService


class RoleController(BaseController):
    """HTTP shaping for role. No rules — see RoleService."""

    service_class = RoleService
