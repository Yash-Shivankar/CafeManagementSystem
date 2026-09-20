"""CustomerFeedbacks endpoints.

HTTP binding only: path, verb, response model. What happens next is
CustomerFeedbackService; how it is fetched is CustomerFeedbackRepository.
"""

from datetime import date

from fastapi import APIRouter, Depends, Query

from app.controllers.customerFeedbackController import CustomerFeedbackController
from app.schemas.customer_feedback import (
    CustomerFeedbackCreate,
    CustomerFeedbackOut,
    CustomerFeedbackUpdate,
    PaginatedCustomerFeedbackOut,
)
from app.utils.pagination import PageParams, page_params

router = APIRouter(prefix="/customer-feedbacks", tags=["CustomerFeedbacks"])


@router.get("/", response_model=PaginatedCustomerFeedbackOut)
def list_feedbacks(
    start_date: date | None = Query(None),
    end_date: date | None = Query(None),
    rating: str | None = Query(None),
    search: str | None = Query(None, min_length=1),
    params: PageParams = Depends(page_params),
    controller: CustomerFeedbackController = Depends(),
):
    return controller.list(
        params,
        search=search,
        start_date=start_date,
        end_date=end_date,
        rating=rating,
    )


@router.get("/{feedback_id}", response_model=CustomerFeedbackOut)
def get_feedback(
    feedback_id: int,
    controller: CustomerFeedbackController = Depends(),
):
    return controller.get(feedback_id)


@router.post("/", response_model=CustomerFeedbackOut)
def create_feedback(
    payload: CustomerFeedbackCreate,
    controller: CustomerFeedbackController = Depends(),
):
    return controller.create(payload)


@router.put("/{feedback_id}", response_model=CustomerFeedbackOut)
def update_feedback(
    feedback_id: int,
    payload: CustomerFeedbackUpdate,
    controller: CustomerFeedbackController = Depends(),
):
    return controller.update(feedback_id, payload)


@router.delete("/{feedback_id}", response_model=CustomerFeedbackOut)
def delete_feedback(
    feedback_id: int,
    controller: CustomerFeedbackController = Depends(),
):
    return controller.delete(feedback_id)
