"""EmployeeDetails endpoints.

HTTP binding only: path, verb, response model. What happens next is
EmployeeDetailsService; how it is fetched is EmployeeDetailsRepository.
"""

from fastapi import APIRouter, Depends, Query

from app.controllers.employeeDetailsController import EmployeeDetailsController
from app.schemas.employee_details import (
    EmployeeDetailsCreate,
    EmployeeDetailsOut,
    EmployeeDetailsUpdate,
    PaginatedEmployeeDetailsOut,
)
from app.utils.pagination import PageParams, page_params

router = APIRouter(prefix="/employee-details", tags=["EmployeeDetails"])


@router.get("/", response_model=PaginatedEmployeeDetailsOut)
def list_employees(
    employment_type: str | None = Query(None),
    department_id: int | None = Query(None),
    designation_id: int | None = Query(None),
    status: str | None = Query(None),
    search: str | None = Query(None, min_length=1),
    params: PageParams = Depends(page_params),
    controller: EmployeeDetailsController = Depends(),
):
    return controller.list(
        params,
        search=search,
        employment_type=employment_type,
        department_id=department_id,
        designation_id=designation_id,
        status=status,
    )


@router.get("/{employee_id}", response_model=EmployeeDetailsOut)
def get_employee(
    employee_id: int,
    controller: EmployeeDetailsController = Depends(),
):
    return controller.get(employee_id)


@router.post("/", response_model=EmployeeDetailsOut)
def create_employee(
    payload: EmployeeDetailsCreate,
    controller: EmployeeDetailsController = Depends(),
):
    return controller.create(payload)


@router.put("/{employee_id}", response_model=EmployeeDetailsOut)
def update_employee(
    employee_id: int,
    payload: EmployeeDetailsUpdate,
    controller: EmployeeDetailsController = Depends(),
):
    return controller.update(employee_id, payload)


@router.delete("/{employee_id}", response_model=EmployeeDetailsOut)
def delete_employee(
    employee_id: int,
    controller: EmployeeDetailsController = Depends(),
):
    return controller.delete(employee_id)
