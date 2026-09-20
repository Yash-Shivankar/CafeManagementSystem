"""SalaryStructures endpoints.

HTTP binding only: path, verb, response model. What happens next is
SalaryStructureService; how it is fetched is SalaryStructureRepository.
"""

from fastapi import APIRouter, Depends

from app.controllers.salaryStructureController import SalaryStructureController
from app.schemas.salary_structure import (
    PaginatedSalaryStructureOut,
    SalaryStructureCreate,
    SalaryStructureOut,
    SalaryStructureUpdate,
)
from app.utils.pagination import PageParams, page_params

router = APIRouter(prefix="/salary-structures", tags=["SalaryStructures"])


@router.get("/", response_model=PaginatedSalaryStructureOut)
def list_salary_structures(
    params: PageParams = Depends(page_params),
    controller: SalaryStructureController = Depends(),
):
    return controller.list(
        params,
    )


@router.get("/{salary_structure_id}", response_model=SalaryStructureOut)
def get_salary_structure(
    salary_structure_id: int,
    controller: SalaryStructureController = Depends(),
):
    return controller.get(salary_structure_id)


@router.post("/", response_model=SalaryStructureOut)
def create_salary_structure(
    payload: SalaryStructureCreate,
    controller: SalaryStructureController = Depends(),
):
    return controller.create(payload)


@router.put("/{salary_structure_id}", response_model=SalaryStructureOut)
def update_salary_structure(
    salary_structure_id: int,
    payload: SalaryStructureUpdate,
    controller: SalaryStructureController = Depends(),
):
    return controller.update(salary_structure_id, payload)


@router.delete("/{salary_structure_id}", response_model=SalaryStructureOut)
def delete_salary_structure(
    salary_structure_id: int,
    controller: SalaryStructureController = Depends(),
):
    return controller.delete(salary_structure_id)
