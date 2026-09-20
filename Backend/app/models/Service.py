from sqlalchemy import Column, ForeignKey, Index, Integer, Numeric, String
from sqlalchemy.orm import relationship

from app.models.Common import Common


class Service(Common):
    __tablename__ = "services"
    __table_args__ = (Index("ix_services_outlet_deleted", "outlet_id", "is_deleted"),)

    id = Column(Integer, primary_key=True, index=True)
    outlet_id = Column(
        Integer,
        ForeignKey("outlets.id"),
        nullable=True,
        index=True,
    )
    name = Column(String(100), nullable=False)
    price = Column(Numeric(10, 2), nullable=False)

    bookings = relationship(
        "Booking",
        foreign_keys="Booking.service_id",
        back_populates="service",
    )

    outlet = relationship("Outlet", foreign_keys=[outlet_id])

    def __repr__(self):
        return f"<Service {self.name} price={self.price}>"
