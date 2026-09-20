from app.models.AuditLog import AuditLog
from app.repositories.baseRepository import BaseRepository


class AuditLogRepository(BaseRepository[AuditLog]):
    """Every audit-trail query and the one write that creates an entry.

    `AuditLog` deliberately does not inherit `Common` — an audit row has no
    `is_deleted`, because a trail you can soft-delete is not a trail — so the
    base query is overridden to drop that filter.
    """

    model = AuditLog
    default_relationships = ("actor",)
    order_by_column = "created_at"
    search_columns = ("table_name", "action", "actor_role", "ip_address")
    search_relations = (("actor", ("first_name", "last_name", "email")),)
    filter_map = {
        "table_name": ("table_name", "eq"),
        "record_id": ("record_id", "eq"),
        "action": ("action", "eq"),
        "actor_id": ("actor_id", "eq"),
        "start_date": ("created_at", "gte"),
        "end_date": ("created_at", "lte"),
    }

    def _base_query(self, relationships=None):
        from sqlalchemy.orm import selectinload

        query = self.db.query(self.model)
        relations = self.default_relationships if relationships is None else relationships
        if relations:
            query = query.options(*[selectinload(getattr(self.model, rel)) for rel in relations])
        return query

    def record(self, entry: AuditLog) -> AuditLog:
        """Added to the caller's transaction, not committed here.

        If the change being recorded rolls back, so does its trail entry — a
        log of things that did not happen is worse than no log.
        """
        self.db.add(entry)
        return entry

    def for_record(self, table_name: str, record_id: int, limit: int = 50):
        return (
            self._base_query()
            .filter(
                AuditLog.table_name == table_name,
                AuditLog.record_id == record_id,
            )
            .order_by(AuditLog.created_at.desc())
            .limit(limit)
            .all()
        )
