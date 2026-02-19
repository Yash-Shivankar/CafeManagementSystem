from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import func
from sqlalchemy.orm import Session
from typing import List
from app.schemas.dashboard import DashboardOut
from app.core.database import get_db
from app.models.User import User
from app.models.Role import Role
from app.models.InventoryItem import InventoryItem


router = APIRouter(prefix="/dashboard", tags=["Dashboard"])


@router.get("/stats", response_model=DashboardOut)
def get_dashboard_stats(db: Session = Depends(get_db)):
    users_count = db.query(func.count(User.id)).filter(User.is_active == True).scalar()
    employees_count = (
        db.query(func.count(User.id))
        .join(User.role)
        .filter(Role.role_name != "Customer")
        .scalar()
    )
    customers_count = (
        db.query(func.count(User.id))
        .join(User.role)
        .filter(Role.role_name == "Customer")
        .scalar()
    )
    items_count = db.query(func.count(InventoryItem.id)).scalar()

    return DashboardOut(
        users_count=users_count,
        employees_count=employees_count,
        customers_count=customers_count,
        items_count=items_count,
    )
