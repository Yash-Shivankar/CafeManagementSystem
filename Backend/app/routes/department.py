"""Departments endpoints.

HTTP binding only: path, verb, response model. What happens next is
DepartmentService; how it is fetched is DepartmentRepository.
"""

from fastapi import APIRouter, Depends, Query

from app.controllers.departmentController import DepartmentController
from app.schemas.department import (
    DepartmentCreate,
    DepartmentOut,
    DepartmentUpdate,
    PaginatedDepartmentOut,
)
from app.utils.pagination import PageParams, page_params

router = APIRouter(prefix="/departments", tags=["Departments"])


@router.get("/", response_model=PaginatedDepartmentOut)
def list_departments(
    search: str | None = Query(None, min_length=1),
    params: PageParams = Depends(page_params),
    controller: DepartmentController = Depends(),
):
    return controller.list(
        params,
        search=search,
    )


@router.get("/{dept_id}", response_model=DepartmentOut)
def get_department(
    dept_id: int,
    controller: DepartmentController = Depends(),
):
    return controller.get(dept_id)


@router.post("/", response_model=DepartmentOut)
def create_department(
    payload: DepartmentCreate,
    controller: DepartmentController = Depends(),
):
    return controller.create(payload)


@router.put("/{dept_id}", response_model=DepartmentOut)
def update_department(
    dept_id: int,
    payload: DepartmentUpdate,
    controller: DepartmentController = Depends(),
):
    return controller.update(dept_id, payload)


@router.delete("/{dept_id}", response_model=DepartmentOut)
def delete_department(
    dept_id: int,
    controller: DepartmentController = Depends(),
):
    return controller.delete(dept_id)
