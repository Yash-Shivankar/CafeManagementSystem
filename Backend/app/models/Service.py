from sqlalchemy import Column, Integer, String, Numeric
from sqlalchemy.orm import relationship
from app.models.Common import Common


class Service(Common):
    __tablename__ = "services"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    price = Column(Numeric(10, 2), nullable=False)

    bookings = relationship(
        "Booking",
        foreign_keys="Booking.service_id",
        back_populates="service",
    )

    def __repr__(self):
        return f"<Service {self.name} price={self.price}>"
