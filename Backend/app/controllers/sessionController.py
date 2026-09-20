from app.controllers.baseController import BaseController
from app.services.sessionService import SessionService


class SessionController(BaseController):
    """HTTP shaping for login sessions. No rules — see SessionService."""

    service_class = SessionService
    service: SessionService

    def revoke(self, session_id: int):
        return self.service.revoke(session_id)
