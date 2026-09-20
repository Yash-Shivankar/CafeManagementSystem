from __future__ import annotations

from sqlalchemy.orm import Session

from app.repositories.dashboardRepository import DashboardRepository


class DashboardService:
    """Read-only summary for the landing screen.

    Does not extend BaseService: there is nothing to create, update or delete
    here, and inheriting a CRUD surface it would never use would be misleading.
    """

    def __init__(self, db: Session, actor=None, outlet_id: int | None = None):
        self.db = db
        self.actor = actor
        self.outlet_id = outlet_id
        self.repository = DashboardRepository(db)

    def stats(self) -> dict:
        outlet_id = self.outlet_id
        return {
            "users_count": self.repository.active_user_count(outlet_id),
            "employees_count": self.repository.employee_count(outlet_id),
            "customers_count": self.repository.customer_count(outlet_id),
            "items_count": self.repository.inventory_item_count(outlet_id),
        }
