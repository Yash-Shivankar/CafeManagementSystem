"""Dashboard endpoints."""

from fastapi import APIRouter, Depends

from app.controllers.dashboardController import DashboardController
from app.schemas.dashboard import DashboardOut

router = APIRouter(prefix="/dashboard", tags=["Dashboard"])


@router.get("/stats", response_model=DashboardOut)
def get_dashboard_stats(controller: DashboardController = Depends()):
    return controller.stats()
