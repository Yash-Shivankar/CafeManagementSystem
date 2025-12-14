from sqlalchemy import (
    Column,
    Integer,
    Text,
    DateTime,
    ForeignKey,
    func,
    CheckConstraint,
)
from sqlalchemy.orm import relationship
from app.models.Common import Common


class CustomerFeedback(Common):
    __tablename__ = "customer_feedback"
    __table_args__ = (
        CheckConstraint("rating BETWEEN 1 AND 5", name="ck_rating_range"),
    )

    id = Column(Integer, primary_key=True, index=True)

    user_id = Column(
        Integer,
        ForeignKey("users.id"),
        nullable=False,
        index=True,
    )

    rating = Column(
        Integer,
        nullable=False,
    )

    feedback = Column(
        Text,
        nullable=True,
    )

    date_given = Column(
        DateTime,
        server_default=func.now(),
        nullable=False,
    )

    user = relationship(
        "User",
        foreign_keys=[user_id],
        back_populates="customer_feedbacks",
    )

    def __repr__(self):
        return f"<CustomerFeedback user={self.user_id} rating={self.rating}>"
