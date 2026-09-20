from sqlalchemy import (
    CheckConstraint,
    Column,
    DateTime,
    ForeignKey,
    Index,
    Integer,
    func,
)
from sqlalchemy import (
    Enum as SQLEnum,
)
from sqlalchemy.orm import relationship

from app.models.Common import Common
from app.models.Enums import BookingStatus, enum_values


class Booking(Common):
    __tablename__ = "bookings"
    __table_args__ = (
        CheckConstraint(
            "(service_id IS NOT NULL) OR (table_id IS NOT NULL)",
            name="ck_booking_service_or_table",
        ),
        Index("ix_bookings_outlet_deleted", "outlet_id", "is_deleted"),
    )

    id = Column(Integer, primary_key=True, index=True)
    outlet_id = Column(
        Integer,
        ForeignKey("outlets.id"),
        nullable=False,
        index=True,
    )

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
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
    )

    status = Column(
        SQLEnum(BookingStatus, name="booking_status_enum", values_callable=enum_values),
        nullable=False,
        default=BookingStatus.SCHEDULED,
    )

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

    outlet = relationship("Outlet", foreign_keys=[outlet_id])

    def __repr__(self):
        return (
            f"<Booking id={self.id} customer={self.user_id} "
            f"staff={self.staff_user_id} status={self.status}>"
        )
