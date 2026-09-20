from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Integer, func
from sqlalchemy.orm import declared_attr, relationship

from app.core.database import Base


class Common(Base):
    __abstract__ = True

    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

    updated_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )

    deleted_at = Column(
        DateTime(timezone=True),
        nullable=True,
    )

    is_deleted = Column(
        Boolean,
        default=False,
        nullable=False,
    )

    created_by = Column(
        Integer,
        ForeignKey("users.id", deferrable=True, initially="DEFERRED"),
        nullable=True,
        comment="User ID who created this record",
    )

    updated_by = Column(
        Integer,
        ForeignKey("users.id", deferrable=True, initially="DEFERRED"),
        nullable=True,
        comment="User ID who last updated this record",
    )

    @declared_attr
    def created_by_user(cls):
        return relationship("User", foreign_keys=[cls.created_by])

    @declared_attr
    def updated_by_user(cls):
        return relationship("User", foreign_keys=[cls.updated_by])
