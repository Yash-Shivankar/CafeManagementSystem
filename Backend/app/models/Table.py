from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship
from app.models.Common import Common


class Table(Common):
    __tablename__ = "tables"

    id = Column(Integer, primary_key=True, index=True)
    table_number = Column(String(20), nullable=False, unique=True)
    seating_capacity = Column(Integer, nullable=False)

    bookings = relationship(
        "Booking",
        foreign_keys="Booking.table_id",
        back_populates="table",
    )

    def __repr__(self):
        return f"<Table {self.table_number} cap={self.seating_capacity}>"
