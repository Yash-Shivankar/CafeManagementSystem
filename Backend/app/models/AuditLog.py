from sqlalchemy import (
    JSON,
    Column,
    DateTime,
    ForeignKey,
    Index,
    Integer,
    String,
    func,
)
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import relationship

from app.core.database import Base


class AuditLog(Base):
    """Who changed what, and what it was before.

    Without this table there is no record of a change at all. `created_by` and
    `updated_by` tell you who touched a row last; they do not tell you that an
    invoice total went from 4,500 to 450, or who moved it, or what it was
    before.

    Deliberately NOT inheriting `Common`. An audit row has no `updated_at`, no
    `updated_by` and no `is_deleted`, because an audit row that can be edited or
    soft-deleted is not an audit row. It is append-only by construction: there
    is no service method that updates or removes one.

    `changes` holds only the fields that actually moved, as
    `{"total_amount": {"from": "4500.00", "to": "450.00"}}` — storing whole
    row snapshots would make the table larger than the data it describes.
    """

    __tablename__ = "audit_logs"
    __table_args__ = (
        Index("ix_audit_logs_record", "table_name", "record_id"),
        Index("ix_audit_logs_outlet_created", "outlet_id", "created_at"),
        Index("ix_audit_logs_actor", "actor_id"),
    )

    id = Column(Integer, primary_key=True, index=True)

    outlet_id = Column(Integer, ForeignKey("outlets.id"), nullable=True, index=True)

    table_name = Column(String(64), nullable=False)
    record_id = Column(Integer, nullable=True)
    action = Column(String(16), nullable=False)

    changes = Column(JSON().with_variant(JSONB, "postgresql"), nullable=True)

    actor_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    actor_role = Column(String(64), nullable=True)
    ip_address = Column(String(64), nullable=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    actor = relationship("User", foreign_keys=[actor_id])
    outlet = relationship("Outlet", foreign_keys=[outlet_id])

    def __repr__(self):
        return f"<AuditLog {self.action} {self.table_name}#{self.record_id} by {self.actor_id}>"
