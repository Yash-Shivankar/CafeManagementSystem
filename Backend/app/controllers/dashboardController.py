from fastapi import Depends
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.dependencies.auth import get_current_outlet, get_current_user
from app.models.User import User
from app.services.dashboardService import DashboardService


class DashboardController:
    """HTTP shaping for the dashboard summary."""

    def __init__(
        self,
        db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user),
        outlet_id: int | None = Depends(get_current_outlet),
    ):
        self.db = db
        self.current_user = current_user
        self.outlet_id = outlet_id
        self.service = DashboardService(db, actor=current_user, outlet_id=outlet_id)

    def stats(self) -> dict:
        return self.service.stats()
