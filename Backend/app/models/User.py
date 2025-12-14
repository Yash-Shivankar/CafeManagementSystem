from sqlalchemy import (
    Column,
    Integer,
    String,
    Boolean,
    Date,
    UniqueConstraint,
    ForeignKey,
)
from sqlalchemy.orm import relationship
from app.models.Common import Common


class User(Common):
    __tablename__ = "users"
    __table_args__ = (
        UniqueConstraint("email", name="uq_users_email"),
        UniqueConstraint("mobile_number", name="uq_users_mobile"),
    )

    id = Column(Integer, primary_key=True, index=True)
    first_name = Column(String(255), nullable=True)
    last_name = Column(String(255), nullable=True)
    email = Column(String(255), nullable=True, index=True)
    mobile_number = Column(String(255), nullable=True, index=True)
    role_id = Column(Integer, ForeignKey("roles.id"), nullable=False)
    hashed_password = Column(String(255), nullable=True)
    date_of_birth = Column(Date, nullable=True)
    gender = Column(String(255), nullable=True)
    is_active = Column(Boolean, default=True)
    is_staff = Column(Boolean, default=False)
    is_superuser = Column(Boolean, default=False)

    role = relationship(
        "Role",
        foreign_keys=[role_id],
        back_populates="users",
    )

    employee_details = relationship(
        "EmployeeDetails",
        foreign_keys="EmployeeDetails.user_id",
        back_populates="user",
        uselist=False,
    )
    customer_feedbacks = relationship(
        "CustomerFeedback",
        foreign_keys="CustomerFeedback.user_id",
        back_populates="user",
        cascade="all, delete-orphan",
    )
    invoices = relationship(
        "CustomerInvoice",
        foreign_keys="CustomerInvoice.user_id",
        back_populates="user",
    )
    customer_bookings = relationship(
        "Booking",
        foreign_keys="Booking.user_id",
        back_populates="customer",
    )

    staff_bookings = relationship(
        "Booking",
        foreign_keys="Booking.staff_user_id",
        back_populates="staff",
    )

    def __repr__(self):
        return f"<User id={self.id} email={self.email}>"
