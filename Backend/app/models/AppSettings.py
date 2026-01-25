from sqlalchemy import Column, Integer, String
from app.models.Common import Common


class AppSettings(Common):
    __tablename__ = "app_settings"

    id = Column(Integer, primary_key=True, index=True)
    key = Column(String(255), nullable=False, unique=True)
    value = Column(String(255), nullable=False)
