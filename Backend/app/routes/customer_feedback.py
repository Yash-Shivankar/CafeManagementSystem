# app/api/customer_feedback.py
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from typing import List
from app.crud.base import CRUDBase
from app.models.CustomerFeedback import CustomerFeedback
from app.schemas.customer_feedback import (
    CustomerFeedbackCreate,
    CustomerFeedbackUpdate,
    CustomerFeedbackOut,
    PaginatedCustomerFeedbackOut,
)
from app.core.database import get_db
from app.dependencies.auth import get_current_user
from math import ceil

router = APIRouter(prefix="/customer-feedbacks", tags=["CustomerFeedbacks"])
feedback_crud = CRUDBase[
    CustomerFeedback, CustomerFeedbackCreate, CustomerFeedbackUpdate
](CustomerFeedback)


@router.post("/", response_model=CustomerFeedbackOut)
def create_feedback(
    feedback_in: CustomerFeedbackCreate,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    return feedback_crud.create(db, obj_in=feedback_in, current_user=current_user)


@router.get("/{feedback_id}", response_model=CustomerFeedbackOut)
def get_feedback(feedback_id: int, db: Session = Depends(get_db)):
    return feedback_crud.get(db, feedback_id)


# @router.get("/", response_model=List[CustomerFeedbackOut])
# def list_feedback(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
#     return feedback_crud.get_multi(db, skip=skip, limit=limit)


@router.get("/", response_model=PaginatedCustomerFeedbackOut)
def list_feedbacks(
    page: int = Query(1, ge=1),
    limit: int = Query(10, ge=1, le=100),
    db: Session = Depends(get_db),
):
    skip = (page - 1) * limit
    feedbacks, total = feedback_crud.get_multi_paginated(db, skip=skip, limit=limit)
    total_pages = ceil(total / limit)
    return {
        "data": feedbacks,
        "total": total,
        "totalPages": total_pages,
        "currentPage": page,
    }


@router.put("/{feedback_id}", response_model=CustomerFeedbackOut)
def update_feedback(
    feedback_id: int,
    feedback_in: CustomerFeedbackUpdate,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    db_feedback = feedback_crud.get(db, feedback_id)
    return feedback_crud.update(
        db, db_feedback, obj_in=feedback_in, current_user=current_user
    )


@router.delete("/{feedback_id}", response_model=CustomerFeedbackOut)
def delete_feedback(
    feedback_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    return feedback_crud.remove(db, feedback_id, current_user=current_user)
