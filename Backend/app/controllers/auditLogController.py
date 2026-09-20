from app.controllers.baseController import BaseController
from app.services.auditLogService import AuditLogService


class AuditLogController(BaseController):
    """HTTP shaping for the audit trail. No rules — see AuditLogService."""

    service_class = AuditLogService
    service: AuditLogService

    def history_for(self, table_name: str, record_id: int):
        return self.service.history_for(table_name, record_id)
