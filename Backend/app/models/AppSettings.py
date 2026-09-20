from sqlalchemy import Column, Index, Integer, String

from app.models.Common import Common


class AppSettings(Common):
    __tablename__ = "app_settings"
    __table_args__ = (Index("ix_app_settings_is_deleted", "is_deleted"),)

    id = Column(Integer, primary_key=True, index=True)
    key = Column(String(255), nullable=False, unique=True)
    value = Column(String(255), nullable=False)
