"""EmployeePerformances endpoints.

HTTP binding only: path, verb, response model. What happens next is
EmployeePerformanceService; how it is fetched is EmployeePerformanceRepository.
"""

from fastapi import APIRouter, Depends, Query

from app.controllers.employeePerformanceController import EmployeePerformanceController
from app.schemas.employee_performance import (
    EmployeePerformanceCreate,
    EmployeePerformanceOut,
    EmployeePerformanceUpdate,
    PaginatedEmployeePerformanceOut,
)
from app.utils.pagination import PageParams, page_params

router = APIRouter(prefix="/employee-performances", tags=["EmployeePerformances"])


@router.get("/", response_model=PaginatedEmployeePerformanceOut)
def list_performances(
    rating: str | None = Query(None),
    search: str | None = Query(None, min_length=1),
    params: PageParams = Depends(page_params),
    controller: EmployeePerformanceController = Depends(),
):
    return controller.list(
        params,
        search=search,
        rating=rating,
    )


@router.get("/{performance_id}", response_model=EmployeePerformanceOut)
def get_performance(
    performance_id: int,
    controller: EmployeePerformanceController = Depends(),
):
    return controller.get(performance_id)


@router.post("/", response_model=EmployeePerformanceOut)
def create_performance(
    payload: EmployeePerformanceCreate,
    controller: EmployeePerformanceController = Depends(),
):
    return controller.create(payload)


@router.put("/{performance_id}", response_model=EmployeePerformanceOut)
def update_performance(
    performance_id: int,
    payload: EmployeePerformanceUpdate,
    controller: EmployeePerformanceController = Depends(),
):
    return controller.update(performance_id, payload)


@router.delete("/{performance_id}", response_model=EmployeePerformanceOut)
def delete_performance(
    performance_id: int,
    controller: EmployeePerformanceController = Depends(),
):
    return controller.delete(performance_id)
