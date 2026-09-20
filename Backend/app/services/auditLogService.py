"""Reading and writing the audit trail.

`write()` is called from `BaseService`'s lifecycle, so every create, update and
delete that goes through a service is recorded without any entity service
opting in. That is the payoff from doing the layering first: there is exactly
one place where writes happen, so there is exactly one place to record them.
"""

from __future__ import annotations

from app.models.AuditLog import AuditLog
from app.repositories.auditLogRepository import AuditLogRepository
from app.services.baseService import BaseService
from app.utils.audit import CREATE, DELETE, UPDATE
from app.utils.exceptions import BusinessRuleError


class AuditLogService(BaseService[AuditLog]):
    """The trail is read-only through the API and append-only in the database.

    There is no create, update or delete: an entry appears because something
    happened, and a record of what happened that someone can rewrite is not a
    record of what happened.
    """

    repository_class = AuditLogRepository
    entity_name = "Audit entry"
    repository: AuditLogRepository

    audited = False

    def scope_filters(self) -> list:
        """Chain-wide roles see everything; a manager sees their own outlet.

        Entries with no outlet (a role being renamed, a user created before any
        branch was chosen) are chain-level and stay with the chain-wide roles.
        """
        if self.is_org_wide:
            return []
        clause = self.repository.outlet_clause(self.outlet_id)
        if clause is not None:
            return [clause]
        return [AuditLog.id == -1]

    def history_for(self, table_name: str, record_id: int, limit: int = 50):
        """Everything that ever happened to one row."""
        return self.repository.for_record(table_name, record_id, limit=limit)

    def before_create(self, data: dict) -> None:
        raise BusinessRuleError(
            "Audit entries are written by the system, not through this endpoint"
        )

    def before_update(self, obj, data: dict) -> None:
        raise BusinessRuleError("An audit entry cannot be edited")

    def before_delete(self, obj) -> None:
        raise BusinessRuleError("An audit entry cannot be deleted")


def write(
    db,
    *,
    action: str,
    table_name: str,
    record_id: int | None,
    changes: dict | None = None,
    actor=None,
    outlet_id: int | None = None,
    ip_address: str | None = None,
) -> AuditLog | None:
    """Add an entry to the caller's open transaction.

    Returns None when there is nothing to say — an update where no field
    actually moved is not an event, and logging it would bury the real ones.
    """
    if action == UPDATE and not changes:
        return None

    role = getattr(getattr(actor, "role", None), "role_name", None)

    return AuditLogRepository(db).record(
        AuditLog(
            table_name=table_name,
            record_id=record_id,
            action=action,
            changes=changes or None,
            actor_id=getattr(actor, "id", None),
            actor_role=role,
            outlet_id=outlet_id,
            ip_address=(ip_address or "")[:64] or None,
        )
    )


__all__ = ["AuditLogService", "write", "CREATE", "UPDATE", "DELETE"]
