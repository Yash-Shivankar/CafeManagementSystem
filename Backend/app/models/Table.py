from sqlalchemy import Column, ForeignKey, Index, Integer, String, UniqueConstraint
from sqlalchemy.orm import relationship

from app.models.Common import Common


class Table(Common):
    __tablename__ = "tables"
    __table_args__ = (
        UniqueConstraint("outlet_id", "table_number", name="uq_tables_outlet_number"),
        Index("ix_tables_outlet_deleted", "outlet_id", "is_deleted"),
    )

    id = Column(Integer, primary_key=True, index=True)
    outlet_id = Column(
        Integer,
        ForeignKey("outlets.id"),
        nullable=False,
        index=True,
    )
    table_number = Column(String(20), nullable=False)
    seating_capacity = Column(Integer, nullable=False)

    bookings = relationship(
        "Booking",
        foreign_keys="Booking.table_id",
        back_populates="table",
    )

    outlet = relationship("Outlet", foreign_keys=[outlet_id])

    def __repr__(self):
        return f"<Table {self.table_number} cap={self.seating_capacity}>"
