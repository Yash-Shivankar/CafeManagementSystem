from app.controllers.baseController import BaseController
from app.services.userService import UserService


class UserController(BaseController):
    """HTTP shaping for users. No rules — see UserService."""

    service_class = UserService
