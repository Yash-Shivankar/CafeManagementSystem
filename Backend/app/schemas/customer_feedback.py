# app/schemas/customer_feedback.py
from datetime import datetime
from typing import Optional, Annotated
from pydantic import BaseModel, Field


class CustomerFeedbackBase(BaseModel):
    user_id: int
    rating: Annotated[int, Field(ge=1, le=5)]
    feedback: Optional[str] = None
    date_given: Optional[datetime] = None  # defaults to now if not provided


class CustomerFeedbackCreate(CustomerFeedbackBase):
    pass  # all fields can be provided


class CustomerFeedbackUpdate(BaseModel):
    rating: Optional[Annotated[int, Field(ge=1, le=5)]] = None
    feedback: Optional[str] = None
    date_given: Optional[datetime] = None


class CustomerFeedbackOut(CustomerFeedbackBase):
    id: int
    created_at: datetime
    updated_at: datetime
    created_by: Optional[int] = None
    updated_by: Optional[int] = None
    deleted_at: Optional[datetime] = None
    is_deleted: Optional[bool] = False

    class Config:
        from_attributes = True
