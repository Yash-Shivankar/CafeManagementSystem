"""EmployeeAttendances endpoints.

HTTP binding only: path, verb, response model. What happens next is
EmployeeAttendanceService; how it is fetched is EmployeeAttendanceRepository.
"""

from datetime import date

from fastapi import APIRouter, Depends, Query

from app.controllers.employeeAttendanceController import EmployeeAttendanceController
from app.schemas.employee_attendance import (
    EmployeeAttendanceCreate,
    EmployeeAttendanceOut,
    EmployeeAttendanceUpdate,
    PaginatedEmployeeAttendanceOut,
)
from app.utils.pagination import PageParams, page_params

router = APIRouter(prefix="/employee-attendances", tags=["EmployeeAttendances"])


@router.get("/", response_model=PaginatedEmployeeAttendanceOut)
def list_attendances(
    start_date: date | None = Query(None),
    end_date: date | None = Query(None),
    session: str | None = Query(None),
    status: str | None = Query(None),
    search: str | None = Query(None, min_length=1),
    params: PageParams = Depends(page_params),
    controller: EmployeeAttendanceController = Depends(),
):
    return controller.list(
        params,
        search=search,
        start_date=start_date,
        end_date=end_date,
        session=session,
        status=status,
    )


@router.get("/{attendance_id}", response_model=EmployeeAttendanceOut)
def get_attendance(
    attendance_id: int,
    controller: EmployeeAttendanceController = Depends(),
):
    return controller.get(attendance_id)


@router.post("/", response_model=EmployeeAttendanceOut)
def create_attendance(
    payload: EmployeeAttendanceCreate,
    controller: EmployeeAttendanceController = Depends(),
):
    return controller.create(payload)


@router.put("/{attendance_id}", response_model=EmployeeAttendanceOut)
def update_attendance(
    attendance_id: int,
    payload: EmployeeAttendanceUpdate,
    controller: EmployeeAttendanceController = Depends(),
):
    return controller.update(attendance_id, payload)


@router.delete("/{attendance_id}", response_model=EmployeeAttendanceOut)
def delete_attendance(
    attendance_id: int,
    controller: EmployeeAttendanceController = Depends(),
):
    return controller.delete(attendance_id)
