from sqlalchemy import (
    Column,
    Integer,
    String,
)
from sqlalchemy.orm import relationship
from app.models.Common import Common


class Role(Common):
    __tablename__ = "roles"

    id = Column(Integer, primary_key=True, index=True)
    role_name = Column(String(255), nullable=False, unique=True, index=True)

    users = relationship(
        "User",
        foreign_keys="User.role_id",
        back_populates="role",
    )

    def __repr__(self):
        return f"<Role id={self.id} role_name={self.role_name}>"
