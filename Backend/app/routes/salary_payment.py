"""SalaryPayments endpoints.

HTTP binding only: path, verb, response model. What happens next is
SalaryPaymentService; how it is fetched is SalaryPaymentRepository.
"""

from fastapi import APIRouter, Depends

from app.controllers.salaryPaymentController import SalaryPaymentController
from app.schemas.salary_payment import (
    PaginatedSalaryPaymentOut,
    PayrollPreview,
    PayrollRequest,
    SalaryPaymentCreate,
    SalaryPaymentOut,
    SalaryPaymentUpdate,
)
from app.utils.pagination import PageParams, page_params

router = APIRouter(prefix="/salary-payments", tags=["SalaryPayments"])


@router.get("/", response_model=PaginatedSalaryPaymentOut)
def list_salary_payments(
    params: PageParams = Depends(page_params),
    controller: SalaryPaymentController = Depends(),
):
    return controller.list(
        params,
    )


@router.post("/preview", response_model=PayrollPreview)
def preview_payroll(
    payload: PayrollRequest,
    controller: SalaryPaymentController = Depends(),
):
    """What this employee is owed for this month, computed from their salary
    structure and their actual attendance — with the workings, and without
    recording anything."""
    return controller.preview(payload.employee_id, payload.month, payload.year)


@router.post("/generate", response_model=SalaryPaymentOut)
def generate_payroll(
    payload: PayrollRequest,
    controller: SalaryPaymentController = Depends(),
):
    """Compute and record. Refuses to pay the same month twice."""
    return controller.generate(payload.employee_id, payload.month, payload.year)


@router.get("/{salary_payment_id}", response_model=SalaryPaymentOut)
def get_salary_payment(
    salary_payment_id: int,
    controller: SalaryPaymentController = Depends(),
):
    return controller.get(salary_payment_id)


@router.post("/", response_model=SalaryPaymentOut)
def create_salary_payment(
    payload: SalaryPaymentCreate,
    controller: SalaryPaymentController = Depends(),
):
    return controller.create(payload)


@router.put("/{salary_payment_id}", response_model=SalaryPaymentOut)
def update_salary_payment(
    salary_payment_id: int,
    payload: SalaryPaymentUpdate,
    controller: SalaryPaymentController = Depends(),
):
    return controller.update(salary_payment_id, payload)


@router.delete("/{salary_payment_id}", response_model=SalaryPaymentOut)
def delete_salary_payment(
    salary_payment_id: int,
    controller: SalaryPaymentController = Depends(),
):
    return controller.delete(salary_payment_id)
