from sqlalchemy import (
    Boolean,
    Column,
    Index,
    Integer,
    String,
    Time,
    UniqueConstraint,
)
from sqlalchemy.orm import relationship

from app.models.Common import Common


class Outlet(Common):
    """A physical cafe location.

    Every transactional row in the system belongs to exactly one outlet. This
    was the cheapest thing to add today and the most expensive thing to add
    later: retrofitting tenancy onto live data means backfilling every table,
    auditing every query, and explaining to the customer why last month's
    reports moved.

    Definitions that a chain shares — roles, departments, designations,
    inventory categories — deliberately have no `outlet_id`. Only events and
    physical things are scoped.

    The GST and FSSAI fields are here because they are per-registration in
    India, not per-company: each outlet files its own GSTR and holds its own
    food licence, so an invoice has to carry the issuing outlet's GSTIN.
    """

    __tablename__ = "outlets"
    __table_args__ = (
        UniqueConstraint("code", name="uq_outlets_code"),
        Index("ix_outlets_is_deleted", "is_deleted"),
    )

    id = Column(Integer, primary_key=True, index=True)

    name = Column(String(255), nullable=False)
    code = Column(String(32), nullable=False, index=True)

    address_line1 = Column(String(255), nullable=True)
    address_line2 = Column(String(255), nullable=True)
    city = Column(String(120), nullable=True)
    state = Column(String(120), nullable=True)
    pincode = Column(String(12), nullable=True)

    phone = Column(String(32), nullable=True)
    email = Column(String(255), nullable=True)

    gstin = Column(String(15), nullable=True)
    fssai_license = Column(String(20), nullable=True)

    opens_at = Column(Time, nullable=True)
    closes_at = Column(Time, nullable=True)

    is_active = Column(Boolean, default=True, nullable=False)

    users = relationship("User", foreign_keys="User.outlet_id", back_populates="outlet")

    def __repr__(self):
        return f"<Outlet id={self.id} code={self.code}>"
