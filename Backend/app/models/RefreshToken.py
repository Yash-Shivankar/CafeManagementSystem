from sqlalchemy import (
    Column,
    DateTime,
    ForeignKey,
    Index,
    Integer,
    String,
    UniqueConstraint,
)
from sqlalchemy.orm import relationship

from app.models.Common import Common


class RefreshToken(Common):
    """One row per issued refresh token.

    Storing the `jti` server-side is what makes logout mean something: without
    it a stolen token stays valid until it expires, and there is no way to cut
    a session short. Rotation on every refresh also turns token theft into a
    detectable event — if an old jti is presented after rotation, the family
    has been compromised.
    """

    __tablename__ = "refresh_tokens"
    __table_args__ = (
        UniqueConstraint("jti", name="refresh_tokens_jti_key"),
        Index("ix_refresh_tokens_user_id", "user_id"),
        Index("ix_refresh_tokens_expires_at", "expires_at"),
    )

    id = Column(Integer, primary_key=True, index=True)
    jti = Column(String(64), nullable=False, unique=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    expires_at = Column(DateTime(timezone=True), nullable=False)
    revoked_at = Column(DateTime(timezone=True), nullable=True)
    replaced_by_jti = Column(String(64), nullable=True)
    user_agent = Column(String(512), nullable=True)
    ip_address = Column(String(64), nullable=True)

    user = relationship("User", foreign_keys=[user_id])

    def __repr__(self):
        return f"<RefreshToken jti={self.jti} user_id={self.user_id}>"
