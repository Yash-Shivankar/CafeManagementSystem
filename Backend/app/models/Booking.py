from sqlalchemy import (
    Column,
    Integer,
    DateTime,
    ForeignKey,
    Enum as SQLEnum,
    CheckConstraint,
    func,
)
from sqlalchemy.orm import relationship
from app.models.Common import Common
from app.models.Enums import BookingStatus


class Booking(Common):
    __tablename__ = "bookings"
    __table_args__ = (
        CheckConstraint(
            "(service_id IS NOT NULL) OR (table_id IS NOT NULL)",
            name="ck_booking_service_or_table",
        ),
    )

    id = Column(Integer, primary_key=True, index=True)

    user_id = Column(
        Integer,
        ForeignKey("users.id"),
        nullable=False,
    )

    staff_user_id = Column(
        Integer,
        ForeignKey("users.id"),
        nullable=True,
    )

    service_id = Column(
        Integer,
        ForeignKey("services.id"),
        nullable=True,
    )

    table_id = Column(
        Integer,
        ForeignKey("tables.id"),
        nullable=True,
    )

    booking_date = Column(
        DateTime,
        nullable=False,
        server_default=func.now(),
    )

    status = Column(
        SQLEnum(BookingStatus, name="booking_status_enum"),
        nullable=False,
        default=BookingStatus.SCHEDULED,
    )

    # Relationships
    customer = relationship(
        "User",
        foreign_keys=[user_id],
        back_populates="customer_bookings",
    )

    staff = relationship(
        "User",
        foreign_keys=[staff_user_id],
        back_populates="staff_bookings",
    )

    service = relationship(
        "Service",
        foreign_keys=[service_id],
        back_populates="bookings",
    )

    table = relationship(
        "Table",
        foreign_keys=[table_id],
        back_populates="bookings",
    )

    def __repr__(self):
        return (
            f"<Booking id={self.id} customer={self.user_id} "
            f"staff={self.staff_user_id} status={self.status}>"
        )
