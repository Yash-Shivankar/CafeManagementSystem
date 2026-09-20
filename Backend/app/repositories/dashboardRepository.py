"""Dashboard aggregates.

Not tied to one table, so it does not extend BaseRepository — but it belongs in
this package all the same, because the rule is that every SQLAlchemy query in
the application lives under `repositories/`.

Every count takes an `outlet_id`. `None` means "the whole chain", which the
service only ever passes for a SuperAdmin or Admin.
"""

from __future__ import annotations

from sqlalchemy import func
from sqlalchemy.orm import Session

from app.models.InventoryItem import InventoryItem
from app.models.Role import Role
from app.models.User import User
from app.utils.permissions import CUSTOMER


class DashboardRepository:
    def __init__(self, db: Session):
        self.db = db

    def _live_users(self, outlet_id: int | None):
        query = self.db.query(func.count(User.id)).filter(User.is_deleted.is_(False))
        if outlet_id is not None:
            query = query.filter(User.outlet_id == outlet_id)
        return query

    def active_user_count(self, outlet_id: int | None = None) -> int:
        return self._live_users(outlet_id).filter(User.is_active.is_(True)).scalar() or 0

    def employee_count(self, outlet_id: int | None = None) -> int:
        return (
            self._live_users(outlet_id).join(User.role).filter(Role.role_name != CUSTOMER).scalar()
            or 0
        )

    def customer_count(self, outlet_id: int | None = None) -> int:
        return (
            self.db.query(func.count(User.id))
            .filter(User.is_deleted.is_(False))
            .join(User.role)
            .filter(Role.role_name == CUSTOMER)
            .scalar()
            or 0
        )

    def inventory_item_count(self, outlet_id: int | None = None) -> int:
        query = self.db.query(func.count(InventoryItem.id)).filter(
            InventoryItem.is_deleted.is_(False)
        )
        if outlet_id is not None:
            query = query.filter(InventoryItem.outlet_id == outlet_id)
        return query.scalar() or 0
