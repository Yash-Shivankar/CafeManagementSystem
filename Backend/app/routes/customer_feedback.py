# app/api/customer_feedback.py
from fastapi import APIRouter, Depends, Query
from sqlalchemy import or_
from sqlalchemy.orm import Session
from datetime import date
from typing import List
from app.crud.base import CRUDBase
from app.models.CustomerFeedback import CustomerFeedback
from app.models.User import User
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
    start_date: date | None = Query(None),
    end_date: date | None = Query(None),
    rating: str | None = Query(None),
    search: str | None = Query(None, min_length=1),
    db: Session = Depends(get_db),
):
    skip = (page - 1) * limit
    filters = []

    if start_date:
        filters.append(CustomerFeedback.date_given >= start_date)
    if end_date:
        filters.append(CustomerFeedback.date_given <= end_date)
    if rating:
        filters.append(CustomerFeedback.rating == rating)

    if search:
        filters.append(
            or_(
                CustomerFeedback.feedback.ilike(f"%{search}%"),
                CustomerFeedback.user.has(
                    or_(
                        User.first_name.ilike(f"%{search}%"),
                        User.last_name.ilike(f"%{search}%"),
                    )
                ),
            )
        )

    feedbacks, total = feedback_crud.get_multi_paginated(
        db, skip=skip, limit=limit, filters=filters
    )
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
